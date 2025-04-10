#!/usr/bin/env python3
"""
This module imports GS1 GPC XML data into an SQLite database.
It parses the XML file, extracts relevant data, and inserts it into the database.
The script is designed to handle the hierarchy of segments, families, classes, bricks,
and attributes. It uses the ElementTree library for XML parsing and SQLite for database
operations. It also includes error handling, logging, and command-line argument parsing.
"""
import sqlite3
import xml.etree.ElementTree as ET
import argparse
import sys
import os
import logging
from datetime import datetime

# --- Configuration ---

# Adjust these tag/attribute names if your GS1 GPC XML file uses different ones
TAG_SEGMENT = 'segment'
TAG_FAMILY = 'family'
TAG_CLASS = 'class'
TAG_BRICK = 'brick'
TAG_ATTRIB_TYPE = 'attType'
TAG_ATTRIB_VALUE = 'attValue'

# Adjust these attribute names if your GS1 GPC XML uses different ones
ATTR_CODE = 'code'
ATTR_TEXT = 'text'
# TODO: Add DEFINITIONS to the database for TAGs that have it
ATTR_DEFINITION = 'definition'
# TODO: Check for 'active' attribute in the XML before inserting into the database
ATTR_ACTIVE = 'active'

# Adjust if your XML root tag is different
EXPECTED_ROOT_TAG = 'schema'

# Default arguments
#DEFAULT_ARG_XML_FILE = './imports/gpc_data_full.xml'            # full feed
DEFAULT_ARG_XML_FILE = './imports/gpc_data.xml'                 # only food/beverage
#DEFAULT_ARG_XML_FILE = './imports/gpc_data_four_family.xml'     # only food/bev only four families
#DEFAULT_ARG_XML_FILE = './imports/gpc_data_single_brick.xml'    # 1 segment 1 family 1 brick
DEFAULT_ARG_DB_FILE = './instances/gpc_data_xml.db'


# --- Logging Setup ---
# Keep your existing logging setup
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

# --- Database Functions ---
# setup_database(), insert_segment(), insert_family(), insert_class(),
# insert_brick(), insert_attribute_type(), and insert_attribute_value()
# function are defined to handle the hierarchy.

def setup_database(db_file_path):
    """
    Connects to the SQLite database and creates GPC tables if they don't exist.

    Args:
        db_file_path (str): The path to the SQLite database file.

    Returns:
        tuple: (sqlite3.Connection, sqlite3.Cursor) or (None, None) on failure.
    """
    logging.info("Attempting to connect to database: %s", db_file_path)
    try:
        # Check if directory exists, create if not
        db_dir = os.path.dirname(db_file_path)
        # Ensure db_dir is not empty (happens if db_path is just a filename)
        # and that the directory doesn't already exist.
        if db_dir and not os.path.exists(db_dir):
            logging.info("Creating directory for database: %s", db_dir)
            os.makedirs(db_dir)

        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()
        logging.info("Database connection successful.")

        # Enable Foreign Key support
        cursor.execute("PRAGMA foreign_keys = ON;")
        logging.info("Foreign key support enabled.")

        # Create tables
        logging.info("Creating tables if they don't exist...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Segments (
            segment_code TEXT PRIMARY KEY,
            description TEXT
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Families (
            family_code TEXT PRIMARY KEY,
            description TEXT,
            segment_code TEXT,
            FOREIGN KEY (segment_code) REFERENCES Segments (segment_code)
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Classes (
            class_code TEXT PRIMARY KEY,
            description TEXT,
            family_code TEXT,
            FOREIGN KEY (family_code) REFERENCES Families (family_code)
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Bricks (
            brick_code TEXT PRIMARY KEY,
            description TEXT,
            class_code TEXT,
            FOREIGN KEY (class_code) REFERENCES Classes (class_code)
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Attribute_Types (
            att_type_code TEXT PRIMARY KEY,
            att_type_text TEXT,
            brick_code TEXT,
            FOREIGN KEY (brick_code) REFERENCES Bricks (brick_code)
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Attribute_Values (
            att_value_code TEXT PRIMARY KEY,
            att_value_text TEXT,
            att_type_code TEXT,
            FOREIGN KEY (att_type_code) REFERENCES Attribute_Types (att_type_code)
        );
        ''')
        logging.info("Tables checked/created successfully.")
        return conn, cursor
    except sqlite3.Error as e:
        logging.error("Database error during setup: %s", e)
        return None, None
    except OSError as e:
        # Log specific error creating directory if it happens
        logging.error("OS error (potentially creating directory %s): %s", db_dir, e)
        return None, None


def insert_segment(cursor, segment_code, description):
    """
    Inserts or ignores a segment record.
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        segment_code (str): The segment code.
        description (str): The segment description.
    Returns:
        bool: True if a row was inserted, False otherwise.
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Segments (segment_code, description)
        VALUES (?, ?);
        ''', (segment_code, description))
        return cursor.rowcount > 0  # Returns True if a row was inserted
    except sqlite3.Error as e:
        logging.error("Error inserting segment %s: %s", segment_code, e)
        return False

def insert_family(cursor, family_code, description, segment_code):
    """
    Inserts or ignores a family record.
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        family_code (str): The family code.
        description (str): The family description.
        segment_code (str): The segment code.
    Returns:
        bool: True if a row was inserted, False otherwise.
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Families (family_code, description, segment_code)
        VALUES (?, ?, ?);
        ''', (family_code, description, segment_code))
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error("Error inserting family %s (Segment %s): %s", family_code, segment_code, e)
        return False

def insert_class(cursor, class_code, description, family_code):
    """
    Inserts or ignores a class record.
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        class_code (str): The class code.
        description (str): The class description.
        family_code (str): The family code.
    Returns:
        bool: True if a row was inserted, False otherwise.
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Classes (class_code, description, family_code)
        VALUES (?, ?, ?);
        ''', (class_code, description, family_code))
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error("Error inserting class %s (Family %s): %s", class_code, family_code, e)
        return False

def insert_brick(cursor, brick_code, description, class_code):
    """
    Inserts or ignores a brick record.
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        brick_code (str): The brick code.
        description (str): The brick description.
        class_code (str): The class code.
    Returns:
        bool: True if a row was inserted, False otherwise.
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Bricks (brick_code, description, class_code)
        VALUES (?, ?, ?);
        ''', (brick_code, description, class_code))
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error("Error inserting brick %s (Class %s): %s", brick_code, class_code, e)
        return False

def insert_attribute_type(cursor, att_type_code, att_type_text, brick_code):
    """
    Inserts an attribute type record.
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        att_type_code (str): The attribute type code.
        att_type_text (str): The attribute type description.
        brick_code (str): The brick code.
    Returns:
        bool: True if a row was inserted, False otherwise.
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Attribute_Types (att_type_code, att_type_text, brick_code)
        VALUES (?, ?, ?);
        ''', (att_type_code, att_type_text, brick_code))
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error("Error inserting attribute type %s: %s", att_type_code, e)
        return False

def insert_attribute_value(cursor, att_value_code, att_value_text, att_type_code):
    """
    Inserts an attribute value record.
    Args:
        cursor (sqlite3.Cursor): The database cursor.
        att_value_code (str): The attribute value code.
        att_value_text (str): The attribute value description.
        att_type_code (str): The attribute type code.
    Returns:
        bool: True if a row was inserted, False otherwise.
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Attribute_Values (att_value_code, att_value_text, att_type_code)
        VALUES (?, ?, ?);
        ''', (att_value_code, att_value_text, att_type_code))
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error("Error inserting attribute value %s: %s", att_value_code, e)
        return False

# --- XML Parsing and Processing Function ---

# pylint: disable=C0301,W0718

def process_gpc_xml(xml_file_path, db_file_path):
    """
    Parses the GS1 GPC XML file and inserts data into the SQLite database,
    following the Segment -> Family -> Class -> Brick hierarchy.

    Args:
        xml_file_path (str): Path to the GS1 GPC XML file.
        db_file_path (str): Path to the SQLite database file.
    """
    logging.info("Starting GS1 GPC XML processing from: %s", xml_file_path)
    logging.info("Target database: %s", db_file_path)

    conn, cursor = None, None  # Initialize to ensure they exist for finally block
    counters = {
        'segments_processed': 0, 'segments_inserted': 0,
        'families_processed': 0, 'families_inserted': 0,
        'classes_processed': 0, 'classes_inserted': 0,
        'bricks_processed': 0, 'bricks_inserted': 0,
        'attribute_types_processed': 0, 'attribute_types_inserted': 0,
        'attribute_values_processed': 0, 'attribute_values_inserted': 0,
    }

    try:
        # 1. Setup Database
        conn, cursor = setup_database(db_file_path)
        if not conn or not cursor:
            logging.error("Database setup failed. Aborting.")
            return # Exit if DB setup fails

        # 2. Parse XML
        logging.info("Parsing XML file: %s...", xml_file_path)
        try:
            # root = ET.parse(xml_file_path).getroot()
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            logging.info("XML parsing successful.")

            # Optional: Log root attributes
            logging.info("Root element: %s", root.tag)
            logging.info("Root attributes: %s", root.attrib)
            # Check if the root element is EXPECTED_ROOT_TAG 'schema'
            if root.tag != EXPECTED_ROOT_TAG:
                raise ValueError("Root element is not <{EXPECTED_ROOT_TAG}> as expected but instead found <{root.tag}>.")

        except ET.ParseError as e:
            logging.error("XML parsing failed: %s", e)
            return # Exit if XML parsing fails
        except FileNotFoundError:
            logging.error("XML file not found: %s", xml_file_path)
            return # Exit if file not found
        except ValueError as e:
            logging.error(
                "XML file does not have the expected structure: %s - %s",
                xml_file_path, e
            )
            return

        # 3. Iterate and Insert Data with corrected Hierarchy
        logging.info("Starting data extraction and insertion...")

        # Determine the correct find expression based on root tag
        # Example: If root is <schema> or similar, direct children are segments.
        # If root is something else, maybe segments are deeper e.g. './/segment'
        # Let's assume segments are direct children for now. Adjust if needed.

        # Find all Segment elements (adjust path if necessary, e.g., './/SegmentList/Segment')
        logging.debug(
            "Looking for elements matching tag '%s' under root <%s>",
            TAG_SEGMENT, root.tag
        )
        segment_elements = root.findall(TAG_SEGMENT)
        if not segment_elements:
            # Try searching deeper if not found as direct children
            logging.debug(
                "No direct children found matching '%s', searching anywhere with './/{TAG_SEGMENT}'",
                 TAG_SEGMENT
         )
            segment_elements = root.findall(f".//{TAG_SEGMENT}")
        # Check if we found any segment elements in second conditional search above and report it
        if not segment_elements:
            logging.warning(
                "No segment elements ('%s') found in the XML file. Check XML structure and TAG_SEGMENT constant.", 
                TAG_SEGMENT
            )

        # --- Start Segment Loop ---
        for segment_elem in segment_elements:
            counters['segments_processed'] += 1
            segment_code = segment_elem.get(ATTR_CODE)
            segment_desc = segment_elem.get(ATTR_TEXT)

            if not segment_code or not segment_desc:
                logging.warning("Skipping Segment element missing code ('%s') or description ('%s').", ATTR_CODE, ATTR_TEXT)
                continue # Skip to the next segment

            logging.debug("Processing Segment: %s - %s", segment_code, segment_desc)
            if insert_segment(cursor, segment_code, segment_desc):
                counters['segments_inserted'] += 1

            # --- Start Family Loop (Nested within Segment) ---
            # Find Family elements *directly under the current segment*
            for family_elem in segment_elem.findall(TAG_FAMILY):
                counters['families_processed'] += 1
                family_code = family_elem.get(ATTR_CODE)
                family_desc = family_elem.get(ATTR_TEXT)

                if not family_code or not family_desc:
                    # # Use ET.tostring carefully, might error on malformed elements
                    # try:
                    #      elem_str = ET.tostring(family_elem, encoding='unicode').strip()
                    #      logging.warning(f"Skipping Family element missing code or description (under Segment {segment_code}): {elem_str}")
                    # except Exception:
                    #      logging.warning(f"Skipping Family element missing code or description (under Segment {segment_code}): [Element details unavailable]")
                    # continue
                    logging.warning("Skipping Family element missing code or description (under Segment %s).", segment_code)
                    continue # Skip to the next family


                logging.debug(
                    "  Processing Family: %s - %s (under Segment %s)",
                    family_code, family_desc, segment_code
                )
                if insert_family(cursor, family_code, family_desc, segment_code):
                    counters['families_inserted'] += 1

                # --- Start Class Loop (Nested within Family) ---
                # Find Class elements *directly under the current family*
                for class_elem in family_elem.findall(TAG_CLASS):
                    counters['classes_processed'] += 1
                    class_code = class_elem.get(ATTR_CODE)
                    class_desc = class_elem.get(ATTR_TEXT)

                    if not class_code or not class_desc:
                        # try:
                        #      elem_str = ET.tostring(class_elem, encoding='unicode').strip()
                        #      logging.warning(f"Skipping Class element missing code or description (under Family {family_code}): {elem_str}")
                        # except Exception:
                        #      logging.warning(f"Skipping Class element missing code or description (under Family {family_code}): [Element details unavailable]")
                        # continue
                        logging.warning("Skipping Class element missing code or description (under Family %s).", family_code)
                        continue # Skip to the next class

                    logging.debug("    Processing Class: %s - %s (under Family %s)", class_code, class_desc, family_code)
                    # Pass the correct family_code to insert_class
                    if insert_class(cursor, class_code, class_desc, family_code):
                        counters['classes_inserted'] += 1

                    # --- Start Brick Loop (Nested within Class) ---
                    # Find Brick elements *directly under the current class*
                    for brick_elem in class_elem.findall(TAG_BRICK):
                        counters['bricks_processed'] += 1
                        brick_code = brick_elem.get(ATTR_CODE)
                        brick_desc = brick_elem.get(ATTR_TEXT)

                        if not brick_code or not brick_desc:
                            # try:
                            #     elem_str = ET.tostring(brick_elem, encoding='unicode').strip()
                            #     logging.warning(f"Skipping Brick element missing code or description (under Class {class_code}): {elem_str}")
                            # except Exception:
                            #     logging.warning(f"Skipping Brick element missing code or description (under Class {class_code}): [Element details unavailable]")
                            # continue
                            logging.warning("Skipping Brick element missing code or description (under Class %s).", class_code)
                            continue # Skip to the next brick

                        logging.debug(
                            "      Processing Brick: %s - %s (under Class %s)",
                            brick_code, brick_desc, class_code
                        )
                        # Pass the correct class_code to insert_brick
                        if insert_brick(cursor, brick_code, brick_desc, class_code):
                            counters['bricks_inserted'] += 1

                        # --- Start Attribute Type Loop (Nested within Brick) ---
                        # Find Attribute Type elements *directly under the current class*
                        for att_type_elem in brick_elem.findall(TAG_ATTRIB_TYPE):
                            counters['attribute_types_processed'] += 1
                            att_type_code = att_type_elem.get(ATTR_CODE)
                            att_type_text = att_type_elem.get(ATTR_TEXT)

                            # if not att_type_code and att_type_text:
                            if not att_type_code or not att_type_text:
                                logging.warning(
                                    "Skipping Attribute Type element missing code or description (under Brick %s).",
                                    brick_code
                                )
                                continue  # Skip to the next attribute type

                            logging.debug(
                                "        Processing Attribute Type: %s - %s (under Brick %s)",
                                att_type_code, att_type_text, brick_code
                            )
                            # Pass the correct brick_code to insert_attribute_type
                            # Note: We assume that the attribute type code is unique across all bricks
                            if insert_attribute_type(cursor, att_type_code, att_type_text, brick_code):
                                counters['attribute_types_inserted'] += 1

                            # --- Start Attribute Values Loop (Nested within Attribute Types) ---
                            for att_value_elem in att_type_elem.findall(TAG_ATTRIB_VALUE):
                                counters['attribute_values_processed'] += 1
                                att_value_code = att_value_elem.get(ATTR_CODE)
                                att_value_text = att_value_elem.get(ATTR_TEXT)

                                # if not att_value_code and att_value_text:
                                if not att_value_code or not att_value_text:
                                    logging.warning(
                                        "Skipping Attribute Value element missing code or description (under Attribute Type %s.",
                                        att_type_code
                                    )
                                    continue  # Skip to the next attribute value

                                logging.debug(
                                    "          Processing Attribute Value: %s - %s (under Attribute Type %s)",
                                    att_value_code, att_value_text, att_type_code
                                )
                                # Pass the correct att_type_code to insert_attribute_value
                                # Note: We assume that the attribute value code is unique across all attribute types
                                # and that the attribute value code is unique across all attribute types
                                if insert_attribute_value(cursor, att_value_code, att_value_text, att_type_code):
                                    counters['attribute_values_inserted'] += 1
                            # --- End Attribute Values Loop ---
                        # --- End Attribute Type Loop ---
                    # --- End Brick Loop ---
                # --- End Class Loop ---
            # --- End Family Loop ---
        # --- End Segment Loop ---

        # 4. Commit changes
        logging.info("Committing changes to the database...")
        conn.commit()
        logging.info("Database commit successful.")

    except Exception as e:
        # Catch any unexpected errors during processing
        logging.error(
            "An unexpected error occurred during processing: %s",
            e, exc_info=True
        ) # Log stack trace
        if conn:
            logging.warning("Rolling back database changes due to error.")
            conn.rollback()

    finally:
        # 5. Close connection
        if conn:
            logging.info("Closing database connection.")
            conn.close()
            logging.info("Database connection closed.")

        # 6. Final Report
        logging.info("--- Import Summary ---")
        logging.info(
            "Segments processed: %s, Inserted (new): %s",
            counters['segments_processed'], counters['segments_inserted']
        )
        logging.info(
            "Families processed: %s, Inserted (new): %s",
            counters['families_processed'], counters['families_inserted']
        )
        logging.info(
            "Classes processed: %s, Inserted (new): %s",
            counters['classes_processed'], counters['classes_inserted']
        )
        logging.info(
            "Bricks processed: %s, Inserted (new): %s",
            counters['bricks_processed'], counters['bricks_inserted']
        )
        logging.info(
            "Attribute Types processed: %s, Inserted (new): %s",
            counters['attribute_types_processed'], counters['attribute_types_inserted']
        )
        logging.info(
            "Attribute Values processed: %s, Inserted (new): %s",
            counters['attribute_values_processed'], counters['attribute_values_inserted']
        )
        logging.info("----------------------")
        logging.info("GS1 GPC XML processing finished.")

# pylint: enable=C0301,W0718


# --- Main Execution Block ---

def main():
    """
    Main function to parse command-line arguments and initiate the import process.
    Uses default values for input and output files if not provided.
    """
    parser = argparse.ArgumentParser(
        description="Import GS1 GPC XML data into an SQLite database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter # Shows defaults in help message
    )

    # Add an XML file argument to specify the input GS1 GPC XML file
    # This allows the user to specify a different XML file if needed.
    # If not provided, it will use the default value defined above.
    # The default value is set to './imports/gpc_data.xml'.
    # This is a smaller subset of the full feed, which is useful for testing.
    # The full feed is much larger and may take longer to process.
    parser.add_argument(
        "--xml-file",
        default = DEFAULT_ARG_XML_FILE,
        help="Path to the input GS1 GPC XML file."
    )

    # Add a database file argument to specify the output SQLite database file
    # This allows the user to specify a different database file if needed.
    # If not provided, it will use the default value defined above.
    # The default value is set to './instances/gpc_data_xml.db'.
    parser.add_argument(
        "--db-file",
        default = DEFAULT_ARG_DB_FILE,
        help="Path to the output SQLite database file (will be created if it doesn't exist)."
    )

    # Add a verbose mode to enable detailed debug logging
    # This is useful for debugging and understanding the flow of the script.
    # It can be enabled by passing the -v or --verbose flag when running the script.
    # This will set the logging level to DEBUG, allowing all debug messages to be shown.
    # This is useful for development and troubleshooting.
    parser.add_argument(
        "-v", "--verbose",
        default=False,
        action="store_true",
        help="Enable detailed debug logging."
    )

    # Add a quiet mode to suppress all logging except errors
    # This is useful for running the script in a production environment
    # where you only want to see critical errors.
    parser.add_argument(
        "-q", "--quiet",
        default=False,
        action="store_true",
        help="Suppress all logging except errors."
    )

    # TODO: Add filter options for hierarchy levels. Example --filter-segment, --filter-family, etc.

    # Parse the command-line arguments
    args = parser.parse_args()

    # --- Logger Level Configuration ---
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.getLogger().setLevel(log_level)
    # Ensure all handlers respect the new level
    for handler in logging.getLogger().handlers:
        handler.setLevel(log_level)
    if args.verbose:
        logging.debug("Verbose logging enabled.")
    # --- End Logger Level Configuration ---

    # Record start time
    start_time = datetime.now()
    logging.info("Script started at: %s", start_time.strftime('%Y-%m-%d %H:%M:%S'))

    # Use the argument attributes (args.xml_file and args.db_file)
    logging.info("Using XML file: %s", args.xml_file)
    logging.info("Using Database file: %s", args.db_file)

    # Run the main processing function
    process_gpc_xml(args.xml_file, args.db_file) # Pass the potentially defaulted values

    # Record end time and duration
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info("Script finished at: %s", end_time.strftime('%Y-%m-%d %H:%M:%S'))
    logging.info("Total execution time: %s", duration)

# This ensures the script runs only if executed directly, not when imported.
if __name__ == "__main__":
    main()

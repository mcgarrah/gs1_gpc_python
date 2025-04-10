import sqlite3
import xml.etree.ElementTree as ET
import argparse
import sys
import os
import logging
from datetime import datetime

# --- Configuration ---

# Adjust these tag/attribute names if your GPC XML uses different ones
TAG_SEGMENT = 'segment'
TAG_FAMILY = 'family'
TAG_CLASS = 'class'
TAG_BRICK = 'brick'
TAG_ATTRIB_TYPE = 'attType'
TAG_ATTRIB_VALUE = 'attValue'

# Adjust these attribute names if your GPC XML uses different ones
ATTR_CODE = 'code'
ATTR_TEXT = 'text'
ATTR_DEFINITION = 'definition'
ATTR_ACTIVE = 'active'

# Adjust if your XML root tag is different
EXPECTED_ROOT_TAG = 'schema'

# Default arguments
DEFAULT_ARG_XML_FILE = './imports/gpc_data_full.xml'            # full feed
#DEFAULT_ARG_XML_FILE = './imports/gpc_data.xml'                 # only food/beverage
#DEFAULT_ARG_XML_FILE = './imports/gpc_data_four_family.xml'     # only food/bev only four families
#DEFAULT_ARG_XML_FILE = './imports/gpc_data_single_brick.xml'    # one segment "food/bev" one family and one brick
DEFAULT_ARG_DB_FILE = './instances/gpc_data_xml.db'


# --- Logging Setup ---
# Keep your existing logging setup
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

# --- Database Functions ---
# Below setup_database, insert_segment, insert_family, insert_class, and insert_brick
# function are defined to handle the hierarchy.

def setup_database(db_file_path):
    """
    Connects to the SQLite database and creates GPC tables if they don't exist.

    Args:
        db_path (str): The path to the SQLite database file.

    Returns:
        tuple: (sqlite3.Connection, sqlite3.Cursor) or (None, None) on failure.
    """
    logging.info(f"Attempting to connect to database: {db_file_path}")
    try:
        # Check if directory exists, create if not
        db_dir = os.path.dirname(db_file_path)
        # Ensure db_dir is not empty (happens if db_path is just a filename)
        # and that the directory doesn't already exist.
        if db_dir and not os.path.exists(db_dir):
            logging.info(f"Creating directory for database: {db_dir}")
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
        logging.error(f"Database error during setup: {e}")
        return None, None
    except OSError as e:
        # Log specific error creating directory if it happens
        logging.error(f"OS error (potentially creating directory {db_dir}): {e}")
        return None, None


def insert_segment(cursor, segment_code, description):
    """Inserts or ignores a segment record."""
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Segments (segment_code, description)
        VALUES (?, ?);
        ''', (segment_code, description))
        return cursor.rowcount > 0 # Returns True if a row was inserted
    except sqlite3.Error as e:
        logging.error(f"Error inserting segment {segment_code}: {e}")
        return False

def insert_family(cursor, family_code, description, segment_code):
    """Inserts or ignores a family record."""
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Families (family_code, description, segment_code)
        VALUES (?, ?, ?);
        ''', (family_code, description, segment_code))
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error inserting family {family_code} (Segment {segment_code}): {e}")
        return False

def insert_class(cursor, class_code, description, family_code):
    """Inserts or ignores a class record."""
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Classes (class_code, description, family_code)
        VALUES (?, ?, ?);
        ''', (class_code, description, family_code))
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error inserting class {class_code} (Family {family_code}): {e}")
        return False

def insert_brick(cursor, brick_code, description, class_code):
    """Inserts or ignores a brick record."""
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Bricks (brick_code, description, class_code)
        VALUES (?, ?, ?);
        ''', (brick_code, description, class_code))
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error inserting brick {brick_code} (Class {class_code}): {e}")
        return False

def insert_attribute_type(cursor, att_type_code, att_type_text, brick_code):
    """Inserts an attribute type record."""
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Attribute_Types (att_type_code, att_type_text, brick_code)
        VALUES (?, ?, ?);
        ''', (att_type_code, att_type_text, brick_code))
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error inserting attribute type {att_type_code}: {e}")
        return False

def insert_attribute_value(cursor, att_value_code, att_value_text, att_type_code):
    """Inserts an attribute value record."""
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO Attribute_Values (att_value_code, att_value_text, att_type_code)
        VALUES (?, ?, ?);
        ''', (att_value_code, att_value_text, att_type_code))
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error inserting attribute value {att_value_code}: {e}")
        return False

# --- XML Parsing and Processing Function ---

def process_gpc_xml(xml_file_path, db_file_path):
    """
    Parses the GPC XML file and inserts data into the SQLite database,
    following the Segment -> Family -> Class -> Brick hierarchy.

    Args:
        xml_file_path (str): Path to the GPC XML file.
        db_file_path (str): Path to the SQLite database file.
    """
    logging.info(f"Starting GPC XML processing from: {xml_file_path}")
    logging.info(f"Target database: {db_file_path}")

    conn, cursor = None, None # Initialize to ensure they exist for finally block
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
        logging.info(f"Parsing XML file: {xml_file_path}...")
        try:
            # root = ET.parse(xml_file_path).getroot()
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            logging.info(f"XML parsing successful.")

            # Optional: Log root attributes
            logging.info(f"Root element: {root.tag}")
            logging.info(f"Root attributes: {root.attrib}")
            # Check if the root element is EXPECTED_ROOT_TAG 'schema'
            if root.tag != EXPECTED_ROOT_TAG:
                raise ValueError("Root element is not <{EXPECTED_ROOT_TAG}> as expected but instead found <{root.tag}>.")

        except ET.ParseError as e:
            logging.error(f"XML parsing failed: {e}")
            return # Exit if XML parsing fails
        except FileNotFoundError:
            logging.error(f"XML file not found: {xml_file_path}")
            return # Exit if file not found
        except ValueError as e:
            logging.error(f"XML file does not have the expected structure: {xml_file_path} - {e}")
            return

        # 3. Iterate and Insert Data with corrected Hierarchy
        logging.info("Starting data extraction and insertion...")

        # Determine the correct find expression based on root tag
        # Example: If root is <schema> or similar, direct children are segments.
        # If root is something else, maybe segments are deeper e.g. './/segment'
        # Let's assume segments are direct children for now. Adjust if needed.

        # Find all Segment elements (adjust path if necessary, e.g., './/SegmentList/Segment')
        logging.debug(f"Looking for elements matching tag '{TAG_SEGMENT}' under root <{root.tag}>")
        segment_elements = root.findall(TAG_SEGMENT)
        if not segment_elements:
            # Try searching deeper if not found as direct children
            logging.debug(f"No direct children found matching '{TAG_SEGMENT}', searching anywhere with './/{TAG_SEGMENT}'")
            segment_elements = root.findall(f".//{TAG_SEGMENT}")
        # Check if we found any segment elements in second conditional search above and report it
        if not segment_elements:
            logging.warning(f"No segment elements ('{TAG_SEGMENT}') found in the XML file. Check XML structure and TAG_SEGMENT constant.")

        # --- Start Segment Loop ---
        for segment_elem in segment_elements:
            counters['segments_processed'] += 1
            segment_code = segment_elem.get(ATTR_CODE)
            segment_desc = segment_elem.get(ATTR_TEXT)

            if not segment_code or not segment_desc:
                logging.warning(f"Skipping Segment element missing code ('{ATTR_CODE}') or description ('{ATTR_TEXT}').")
                continue # Skip to the next segment

            logging.debug(f"Processing Segment: {segment_code} - {segment_desc}")
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
                    logging.warning(f"Skipping Family element missing code or description (under Segment {segment_code}).")
                    continue # Skip to the next family


                logging.debug(f"  Processing Family: {family_code} - {family_desc} (under Segment {segment_code})")
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
                        logging.warning(f"Skipping Class element missing code or description (under Family {family_code}).")
                        continue # Skip to the next class

                    logging.debug(f"    Processing Class: {class_code} - {class_desc} (under Family {family_code})")
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
                            logging.warning(f"Skipping Brick element missing code or description (under Class {class_code}).")
                            continue # Skip to the next brick

                        logging.debug(f"      Processing Brick: {brick_code} - {brick_desc} (under Class {class_code})")
                        # Pass the correct class_code to insert_brick
                        if insert_brick(cursor, brick_code, brick_desc, class_code):
                            counters['bricks_inserted'] += 1

                        # --- Start Attribute Type Loop (Nested within Brick) ---
                        # Find Attribute Type elements *directly under the current class*
                        for att_type_elem in brick_elem.findall(TAG_ATTRIB_TYPE):
                            counters['attribute_types_processed'] += 1
                            att_type_code = att_type_elem.get(ATTR_CODE)
                            att_type_text = att_type_elem.get(ATTR_TEXT)

                            if not att_type_code and att_type_text:
                                logging.warning(f"Skipping Attribute Type element missing code or description (under Brick {brick_code}).")
                                continue # Skip to the next attribute type

                            logging.debug(f"        Processing Attribute Type: {att_type_code} - {att_type_text} (under Brick {brick_code})")
                            # Pass the correct brick_code to insert_attribute_type
                            # Note: We assume that the attribute type code is unique across all bricks
                            if insert_attribute_type(cursor, att_type_code, att_type_text, brick_code):
                                counters['attribute_types_inserted'] += 1

                            # --- Start Attribute Values Loop (Nested within Attribute Types) ---
                            for att_value_elem in att_type_elem.findall(TAG_ATTRIB_VALUE):
                                counters['attribute_values_processed'] += 1
                                att_value_code = att_value_elem.get(ATTR_CODE)
                                att_value_text = att_value_elem.get(ATTR_TEXT)

                                if not att_value_code and att_value_text:
                                    logging.warning(f"Skipping Attribute Value element missing code or description (under Attribute Type {att_type_code}).")
                                    continue # Skip to the next attribute value

                                logging.debug(f"          Processing Attribute Value: {att_value_code} - {att_value_text} (under Attribute Type {att_type_code})")
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
        logging.error(f"An unexpected error occurred during processing: {e}", exc_info=True) # Log stack trace
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
        logging.info(f"Segments processed: {counters['segments_processed']}, Inserted (new): {counters['segments_inserted']}")
        logging.info(f"Families processed: {counters['families_processed']}, Inserted (new): {counters['families_inserted']}")
        logging.info(f"Classes processed: {counters['classes_processed']}, Inserted (new): {counters['classes_inserted']}")
        logging.info(f"Bricks processed: {counters['bricks_processed']}, Inserted (new): {counters['bricks_inserted']}")
        logging.info(f"Attribute Types processed: {counters['attribute_types_processed']}, Inserted (new): {counters['attribute_types_inserted']}")
        logging.info(f"Attribute Values processed: {counters['attribute_values_processed']}, Inserted (new): {counters['attribute_values_inserted']}")
        logging.info("----------------------")
        logging.info("GPC XML processing finished.")


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

    parser.add_argument(
        "--xml-file",  # Optional argument
        # default="./imports/gpc_data_single.xml", # Default value
        default = DEFAULT_ARG_XML_FILE,
        help="Path to the input GS1 GPC XML file."
    )

    parser.add_argument(
        "--db-file",   # Optional argument
        # default="./instances/gpc_data_xml.db",  # Default value
        default = DEFAULT_ARG_DB_FILE,
        help="Path to the output SQLite database file (will be created if it doesn't exist)."
    )

    parser.add_argument(
        "-v", "--verbose",
        default=True,
        action="store_true",
        help="Enable detailed debug logging."
    )

    args = parser.parse_args()

    # --- Logger Level Configuration ---
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(log_level)
    # Ensure all handlers respect the new level
    for handler in logging.getLogger().handlers:
        handler.setLevel(log_level)
    if args.verbose:
        logging.debug("Verbose logging enabled.")
    # --- End Logger Level Configuration ---

    # Record start time
    start_time = datetime.now()
    logging.info(f"Script started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Use the argument attributes (args.xml_file and args.db_file)
    logging.info(f"Using XML file: {args.xml_file}")
    logging.info(f"Using Database file: {args.db_file}")

    # Run the main processing function
    process_gpc_xml(args.xml_file, args.db_file) # Pass the potentially defaulted values

    # Record end time and duration
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"Script finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Total execution time: {duration}")

# This ensures the script runs only if executed directly, not when imported.
if __name__ == "__main__":
    main()

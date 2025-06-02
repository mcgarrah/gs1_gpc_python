"""
XML parsing functionality for GS1 GPC.

This module provides classes for parsing GS1 GPC XML data and inserting it into a database.

The main class is GPCParser which handles parsing GPC XML files and inserting the data
into a database. It supports callbacks for custom processing of GPC elements.
A legacy function is provided for backward compatibility but new code should use
the GPCParser class.
"""

import logging
import xml.etree.ElementTree as ET
from .db import (
    insert_segment, insert_family, insert_class, insert_brick,
    insert_attribute_type, insert_attribute_value
)
from .models import GPCModels
from .callbacks import GPCProcessedCallback

# XML tag and attribute names
TAG_SEGMENT = 'segment'
TAG_FAMILY = 'family'
TAG_CLASS = 'class'
TAG_BRICK = 'brick'
TAG_ATTRIB_TYPE = 'attType'
TAG_ATTRIB_VALUE = 'attValue'
ATTR_CODE = 'code'
ATTR_TEXT = 'text'
EXPECTED_ROOT_TAG = 'schema'


class GPCParser:
    """
    Class for parsing GS1 GPC XML data and inserting it into a database.
    
    This class handles the parsing of GPC XML files and inserting the data into
    a database. It processes the hierarchical structure of GPC data (segments,
    families, classes, bricks, attribute types, and attribute values) and maintains
    counters for tracking the processing statistics.
    
    It also supports callbacks for custom processing of GPC elements through the
    GPCProcessedCallback interface.
    """
    
    def __init__(self, db_connection, callback=None):
        """
        Initialize a GPCParser.
        
        Args:
            db_connection: Database connection object
            callback (GPCProcessedCallback, optional): Callback for processing events
        """
        self.db_connection = db_connection
        self.callback = callback
        self.models = GPCModels()
        self.counters = {
            'segments_processed': 0, 'segments_inserted': 0,
            'families_processed': 0, 'families_inserted': 0,
            'classes_processed': 0, 'classes_inserted': 0,
            'bricks_processed': 0, 'bricks_inserted': 0,
            'attribute_types_processed': 0, 'attribute_types_inserted': 0,
            'attribute_values_processed': 0, 'attribute_values_inserted': 0,
        }
    
    def process_xml(self, xml_file_path):
        """
        Parse GS1 GPC XML file and insert data into the database.
        
        This method parses the GPC XML file, validates its structure, and processes
        all GPC elements (segments, families, classes, bricks, attribute types, and
        attribute values). It inserts the data into the database and builds an in-memory
        model of the GPC hierarchy.
        
        If a callback is provided, it will be called for each element processed and
        when processing is complete.
        
        Args:
            xml_file_path (str): Path to the GS1 GPC XML file
            
        Returns:
            dict: Counters with processing statistics (items processed and inserted)
        """
        logging.info("Starting GS1 GPC XML processing from: %s", xml_file_path)
        
        conn, cursor = None, None
        
        try:
            # Setup database connection
            conn, cursor = self.db_connection.connect()
            if not conn or not cursor:
                logging.error("Database connection failed. Aborting.")
                return self.counters
                
            # Parse XML
            logging.info("Parsing XML file: %s...", xml_file_path)
            try:
                tree = ET.parse(xml_file_path)
                root = tree.getroot()
                logging.info("XML parsing successful.")
                
                # Check root element
                if root.tag != EXPECTED_ROOT_TAG:
                    raise ValueError(f"Root element is not <{EXPECTED_ROOT_TAG}> as expected but instead found <{root.tag}>.")
                    
            except ET.ParseError as e:
                logging.error("XML parsing failed: %s", e)
                return self.counters
            except FileNotFoundError:
                logging.error("XML file not found: %s", xml_file_path)
                return self.counters
            except ValueError as e:
                logging.error("XML file does not have the expected structure: %s - %s", xml_file_path, e)
                return self.counters
                
            # Find segment elements
            segment_elements = root.findall(TAG_SEGMENT)
            if not segment_elements:
                segment_elements = root.findall(f".//{TAG_SEGMENT}")
                
            if not segment_elements:
                logging.warning("No segment elements found in the XML file.")
                return self.counters
                
            # Process segments
            for segment_elem in segment_elements:
                self._process_segment(cursor, segment_elem)
            
            # Commit changes
            self.db_connection.commit()
            logging.info("Database commit successful.")
            
        except Exception as e:
            logging.error("An unexpected error occurred during processing: %s", e, exc_info=True)
            if conn:
                self.db_connection.rollback()
        
        finally:
            # Log summary
            self._log_summary()
            
            # Call completion callback if provided
            if self.callback:
                self.callback.on_processing_complete(self.counters)
            
        return self.counters
    
    def _process_segment(self, cursor, segment_elem):
        """
        Process a segment element and its children.
        
        Extracts segment code and description, inserts into database,
        adds to the models container, and processes child family elements.
        """
        self.counters['segments_processed'] += 1
        segment_code = segment_elem.get(ATTR_CODE)
        segment_desc = segment_elem.get(ATTR_TEXT)
        
        if not segment_code or not segment_desc:
            logging.warning("Skipping segment element missing code or description.")
            return
            
        is_new = insert_segment(cursor, segment_code, segment_desc)
        if is_new:
            self.counters['segments_inserted'] += 1
        
        # Add to models
        segment = GPCModels.Segment(segment_code, segment_desc)
        self.models.segments[segment_code] = segment
        
        # Call callback if provided
        if self.callback:
            self.callback.on_segment_processed(segment_code, segment_desc, is_new)
            
        # Process families
        for family_elem in segment_elem.findall(TAG_FAMILY):
            self._process_family(cursor, family_elem, segment_code)
    
    def _process_family(self, cursor, family_elem, segment_code):
        """
        Process a family element and its children.
        
        Extracts family code and description, inserts into database with parent segment code,
        adds to the models container, and processes child class elements.
        """
        self.counters['families_processed'] += 1
        family_code = family_elem.get(ATTR_CODE)
        family_desc = family_elem.get(ATTR_TEXT)
        
        if not family_code or not family_desc:
            logging.warning("Skipping family element missing code or description.")
            return
            
        is_new = insert_family(cursor, family_code, family_desc, segment_code)
        if is_new:
            self.counters['families_inserted'] += 1
        
        # Add to models
        family = GPCModels.Family(family_code, family_desc, segment_code)
        self.models.segments[segment_code].families[family_code] = family
        
        # Call callback if provided
        if self.callback:
            self.callback.on_family_processed(family_code, family_desc, segment_code, is_new)
            
        # Process classes
        for class_elem in family_elem.findall(TAG_CLASS):
            self._process_class(cursor, class_elem, family_code, segment_code)
    
    def _process_class(self, cursor, class_elem, family_code, segment_code):
        """
        Process a class element and its children.
        
        Extracts class code and description, inserts into database with parent family code,
        adds to the models container, and processes child brick elements.
        """
        self.counters['classes_processed'] += 1
        class_code = class_elem.get(ATTR_CODE)
        class_desc = class_elem.get(ATTR_TEXT)
        
        if not class_code or not class_desc:
            logging.warning("Skipping class element missing code or description.")
            return
            
        is_new = insert_class(cursor, class_code, class_desc, family_code)
        if is_new:
            self.counters['classes_inserted'] += 1
        
        # Add to models
        class_obj = GPCModels.Class(class_code, class_desc, family_code)
        self.models.segments[segment_code].families[family_code].classes[class_code] = class_obj
        
        # Call callback if provided
        if self.callback:
            self.callback.on_class_processed(class_code, class_desc, family_code, is_new)
            
        # Process bricks
        for brick_elem in class_elem.findall(TAG_BRICK):
            self._process_brick(cursor, brick_elem, class_code, family_code, segment_code)
    
    def _process_brick(self, cursor, brick_elem, class_code, family_code, segment_code):
        """
        Process a brick element and its children.
        
        Extracts brick code and description, inserts into database with parent class code,
        adds to the models container, and processes child attribute type elements.
        Bricks are the fundamental building blocks of the GPC system.
        """
        self.counters['bricks_processed'] += 1
        brick_code = brick_elem.get(ATTR_CODE)
        brick_desc = brick_elem.get(ATTR_TEXT)
        
        if not brick_code or not brick_desc:
            logging.warning("Skipping brick element missing code or description.")
            return
            
        is_new = insert_brick(cursor, brick_code, brick_desc, class_code)
        if is_new:
            self.counters['bricks_inserted'] += 1
        
        # Add to models
        brick = GPCModels.Brick(brick_code, brick_desc, class_code)
        self.models.segments[segment_code].families[family_code].classes[class_code].bricks[brick_code] = brick
        
        # Call callback if provided
        if self.callback:
            self.callback.on_brick_processed(brick_code, brick_desc, class_code, is_new)
            
        # Process attribute types
        for att_type_elem in brick_elem.findall(TAG_ATTRIB_TYPE):
            self._process_attribute_type(cursor, att_type_elem, brick_code, class_code, family_code, segment_code)
    
    def _process_attribute_type(self, cursor, att_type_elem, brick_code, class_code, family_code, segment_code):
        """
        Process an attribute type element and its children.
        
        Extracts attribute type code and description, inserts into database with parent brick code,
        adds to the models container, and processes child attribute value elements.
        Attribute types define categories of attributes that can be assigned to bricks.
        """
        self.counters['attribute_types_processed'] += 1
        att_type_code = att_type_elem.get(ATTR_CODE)
        att_type_text = att_type_elem.get(ATTR_TEXT)
        
        if not att_type_code or not att_type_text:
            logging.warning("Skipping attribute type element missing code or description.")
            return
            
        is_new = insert_attribute_type(cursor, att_type_code, att_type_text, brick_code)
        if is_new:
            self.counters['attribute_types_inserted'] += 1
        
        # Add to models
        att_type = GPCModels.AttributeType(att_type_code, att_type_text, brick_code)
        self.models.segments[segment_code].families[family_code].classes[class_code].bricks[brick_code].attribute_types[att_type_code] = att_type
        
        # Call callback if provided
        if self.callback:
            self.callback.on_attribute_type_processed(att_type_code, att_type_text, brick_code, is_new)
            
        # Process attribute values
        for att_value_elem in att_type_elem.findall(TAG_ATTRIB_VALUE):
            self._process_attribute_value(cursor, att_value_elem, att_type_code, brick_code, class_code, family_code, segment_code)
    
    def _process_attribute_value(self, cursor, att_value_elem, att_type_code, brick_code, class_code, family_code, segment_code):
        """
        Process an attribute value element.
        
        Extracts attribute value code and description, inserts into database with parent attribute type code,
        and adds to the models container. Attribute values are specific values that can be assigned to
        attribute types for a particular brick.
        """
        self.counters['attribute_values_processed'] += 1
        att_value_code = att_value_elem.get(ATTR_CODE)
        att_value_text = att_value_elem.get(ATTR_TEXT)
        
        if not att_value_code or not att_value_text:
            logging.warning("Skipping attribute value element missing code or description.")
            return
            
        is_new = insert_attribute_value(cursor, att_value_code, att_value_text, att_type_code)
        if is_new:
            self.counters['attribute_values_inserted'] += 1
        
        # Add to models
        att_value = GPCModels.AttributeValue(att_value_code, att_value_text, att_type_code)
        self.models.segments[segment_code].families[family_code].classes[class_code].bricks[brick_code].attribute_types[att_type_code].attribute_values[att_value_code] = att_value
        
        # Call callback if provided
        if self.callback:
            self.callback.on_attribute_value_processed(att_value_code, att_value_text, att_type_code, is_new)
    
    def _log_summary(self):
        """
        Log processing summary.
        
        Outputs a summary of the processing statistics, including the number of
        segments, families, classes, bricks, attribute types, and attribute values
        that were processed and inserted.
        """
        logging.info("--- Import Summary ---")
        logging.info("Segments processed: %s, Inserted (new): %s", 
                    self.counters['segments_processed'], self.counters['segments_inserted'])
        logging.info("Families processed: %s, Inserted (new): %s", 
                    self.counters['families_processed'], self.counters['families_inserted'])
        logging.info("Classes processed: %s, Inserted (new): %s", 
                    self.counters['classes_processed'], self.counters['classes_inserted'])
        logging.info("Bricks processed: %s, Inserted (new): %s", 
                    self.counters['bricks_processed'], self.counters['bricks_inserted'])
        logging.info("Attribute Types processed: %s, Inserted (new): %s", 
                    self.counters['attribute_types_processed'], self.counters['attribute_types_inserted'])
        logging.info("Attribute Values processed: %s, Inserted (new): %s", 
                    self.counters['attribute_values_processed'], self.counters['attribute_values_inserted'])
        logging.info("GS1 GPC XML processing finished.")


# Legacy function for backward compatibility
def process_gpc_xml(xml_file_path, db_connection, callback=None):
    """
    Parse GS1 GPC XML file and insert data into the database.
    
    This is a legacy function maintained for backward compatibility.
    New code should use the GPCParser class instead.
    
    Args:
        xml_file_path (str): Path to the GS1 GPC XML file
        db_connection: Database connection object
        callback (GPCProcessedCallback, optional): Callback for processing events
        
    Returns:
        dict: Counters with processing statistics
    """
    parser = GPCParser(db_connection, callback)
    return parser.process_xml(xml_file_path)
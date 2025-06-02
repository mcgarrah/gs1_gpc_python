"""
XML parsing functionality for GS1 GPC.

This module provides functions for parsing GS1 GPC XML data and inserting it into a database.
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


def process_gpc_xml(xml_file_path, db_connection, callback=None):
    """
    Parse GS1 GPC XML file and insert data into the database.
    
    Args:
        xml_file_path (str): Path to the GS1 GPC XML file
        db_connection: Database connection object
        callback (GPCProcessedCallback, optional): Callback for processing events
        
    Returns:
        dict: Counters with processing statistics
    """
    logging.info("Starting GS1 GPC XML processing from: %s", xml_file_path)
    
    conn, cursor = None, None
    counters = {
        'segments_processed': 0, 'segments_inserted': 0,
        'families_processed': 0, 'families_inserted': 0,
        'classes_processed': 0, 'classes_inserted': 0,
        'bricks_processed': 0, 'bricks_inserted': 0,
        'attribute_types_processed': 0, 'attribute_types_inserted': 0,
        'attribute_values_processed': 0, 'attribute_values_inserted': 0,
    }
    
    # Initialize models container
    models = GPCModels()
    
    try:
        # Setup database connection
        conn, cursor = db_connection.connect()
        if not conn or not cursor:
            logging.error("Database connection failed. Aborting.")
            return counters
            
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
            return counters
        except FileNotFoundError:
            logging.error("XML file not found: %s", xml_file_path)
            return counters
        except ValueError as e:
            logging.error("XML file does not have the expected structure: %s - %s", xml_file_path, e)
            return counters
            
        # Find segment elements
        segment_elements = root.findall(TAG_SEGMENT)
        if not segment_elements:
            segment_elements = root.findall(f".//{TAG_SEGMENT}")
            
        if not segment_elements:
            logging.warning("No segment elements found in the XML file.")
            return counters
            
        # Process segments
        for segment_elem in segment_elements:
            counters['segments_processed'] += 1
            segment_code = segment_elem.get(ATTR_CODE)
            segment_desc = segment_elem.get(ATTR_TEXT)
            
            if not segment_code or not segment_desc:
                logging.warning("Skipping segment element missing code or description.")
                continue
                
            is_new = insert_segment(cursor, segment_code, segment_desc)
            if is_new:
                counters['segments_inserted'] += 1
            
            # Add to models
            segment = GPCModels.Segment(segment_code, segment_desc)
            models.segments[segment_code] = segment
            
            # Call callback if provided
            if callback:
                callback.on_segment_processed(segment_code, segment_desc, is_new)
                
            # Process families
            for family_elem in segment_elem.findall(TAG_FAMILY):
                counters['families_processed'] += 1
                family_code = family_elem.get(ATTR_CODE)
                family_desc = family_elem.get(ATTR_TEXT)
                
                if not family_code or not family_desc:
                    logging.warning("Skipping family element missing code or description.")
                    continue
                    
                is_new = insert_family(cursor, family_code, family_desc, segment_code)
                if is_new:
                    counters['families_inserted'] += 1
                
                # Add to models
                family = GPCModels.Family(family_code, family_desc, segment_code)
                models.segments[segment_code].families[family_code] = family
                
                # Call callback if provided
                if callback:
                    callback.on_family_processed(family_code, family_desc, segment_code, is_new)
                    
                # Process classes
                for class_elem in family_elem.findall(TAG_CLASS):
                    counters['classes_processed'] += 1
                    class_code = class_elem.get(ATTR_CODE)
                    class_desc = class_elem.get(ATTR_TEXT)
                    
                    if not class_code or not class_desc:
                        logging.warning("Skipping class element missing code or description.")
                        continue
                        
                    is_new = insert_class(cursor, class_code, class_desc, family_code)
                    if is_new:
                        counters['classes_inserted'] += 1
                    
                    # Add to models
                    class_obj = GPCModels.Class(class_code, class_desc, family_code)
                    models.segments[segment_code].families[family_code].classes[class_code] = class_obj
                    
                    # Call callback if provided
                    if callback:
                        callback.on_class_processed(class_code, class_desc, family_code, is_new)
                        
                    # Process bricks
                    for brick_elem in class_elem.findall(TAG_BRICK):
                        counters['bricks_processed'] += 1
                        brick_code = brick_elem.get(ATTR_CODE)
                        brick_desc = brick_elem.get(ATTR_TEXT)
                        
                        if not brick_code or not brick_desc:
                            logging.warning("Skipping brick element missing code or description.")
                            continue
                            
                        is_new = insert_brick(cursor, brick_code, brick_desc, class_code)
                        if is_new:
                            counters['bricks_inserted'] += 1
                        
                        # Add to models
                        brick = GPCModels.Brick(brick_code, brick_desc, class_code)
                        models.segments[segment_code].families[family_code].classes[class_code].bricks[brick_code] = brick
                        
                        # Call callback if provided
                        if callback:
                            callback.on_brick_processed(brick_code, brick_desc, class_code, is_new)
                            
                        # Process attribute types
                        for att_type_elem in brick_elem.findall(TAG_ATTRIB_TYPE):
                            counters['attribute_types_processed'] += 1
                            att_type_code = att_type_elem.get(ATTR_CODE)
                            att_type_text = att_type_elem.get(ATTR_TEXT)
                            
                            if not att_type_code or not att_type_text:
                                logging.warning("Skipping attribute type element missing code or description.")
                                continue
                                
                            is_new = insert_attribute_type(cursor, att_type_code, att_type_text, brick_code)
                            if is_new:
                                counters['attribute_types_inserted'] += 1
                            
                            # Add to models
                            att_type = GPCModels.AttributeType(att_type_code, att_type_text, brick_code)
                            models.segments[segment_code].families[family_code].classes[class_code].bricks[brick_code].attribute_types[att_type_code] = att_type
                            
                            # Call callback if provided
                            if callback:
                                callback.on_attribute_type_processed(att_type_code, att_type_text, brick_code, is_new)
                                
                            # Process attribute values
                            for att_value_elem in att_type_elem.findall(TAG_ATTRIB_VALUE):
                                counters['attribute_values_processed'] += 1
                                att_value_code = att_value_elem.get(ATTR_CODE)
                                att_value_text = att_value_elem.get(ATTR_TEXT)
                                
                                if not att_value_code or not att_value_text:
                                    logging.warning("Skipping attribute value element missing code or description.")
                                    continue
                                    
                                is_new = insert_attribute_value(cursor, att_value_code, att_value_text, att_type_code)
                                if is_new:
                                    counters['attribute_values_inserted'] += 1
                                
                                # Add to models
                                att_value = GPCModels.AttributeValue(att_value_code, att_value_text, att_type_code)
                                models.segments[segment_code].families[family_code].classes[class_code].bricks[brick_code].attribute_types[att_type_code].attribute_values[att_value_code] = att_value
                                
                                # Call callback if provided
                                if callback:
                                    callback.on_attribute_value_processed(att_value_code, att_value_text, att_type_code, is_new)
        
        # Commit changes
        db_connection.commit()
        logging.info("Database commit successful.")
        
    except Exception as e:
        logging.error("An unexpected error occurred during processing: %s", e, exc_info=True)
        if conn:
            db_connection.rollback()
    
    finally:
        # Log summary
        logging.info("--- Import Summary ---")
        logging.info("Segments processed: %s, Inserted (new): %s", 
                    counters['segments_processed'], counters['segments_inserted'])
        logging.info("Families processed: %s, Inserted (new): %s", 
                    counters['families_processed'], counters['families_inserted'])
        logging.info("Classes processed: %s, Inserted (new): %s", 
                    counters['classes_processed'], counters['classes_inserted'])
        logging.info("Bricks processed: %s, Inserted (new): %s", 
                    counters['bricks_processed'], counters['bricks_inserted'])
        logging.info("Attribute Types processed: %s, Inserted (new): %s", 
                    counters['attribute_types_processed'], counters['attribute_types_inserted'])
        logging.info("Attribute Values processed: %s, Inserted (new): %s", 
                    counters['attribute_values_processed'], counters['attribute_values_inserted'])
        logging.info("GS1 GPC XML processing finished.")
        
        # Call completion callback if provided
        if callback:
            callback.on_processing_complete(counters)
        
    return counters
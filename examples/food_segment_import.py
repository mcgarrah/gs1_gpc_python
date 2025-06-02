#!/usr/bin/env python3
"""
Advanced example script demonstrating how to import only the Food/Beverage segment (50000000)
from GS1 GPC data.
"""

import os
import logging
import xml.etree.ElementTree as ET
from gs1_gpc.db import DatabaseConnection, setup_database
from gs1_gpc.parser import GPCParser
from gs1_gpc.downloader import GPCDownloader
from gs1_gpc.callbacks import GPCProcessedCallback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Get script directory
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define paths
GPC_DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, 'data', 'imports')
DB_FILE = os.path.join(SCRIPT_DIR, 'data', 'instances', 'food_segment_import.sqlite3')

# Define the Food/Beverage segment code
FOOD_SEGMENT_CODE = "50000000"


class FoodSegmentFilter(GPCProcessedCallback):
    """Callback to filter and process only the Food/Beverage segment."""
    
    def __init__(self):
        self.stats = {
            'families': 0,
            'classes': 0,
            'bricks': 0,
            'attribute_types': 0,
            'attribute_values': 0
        }
    
    def on_segment_processed(self, segment_code, segment_desc, is_new):
        """Only allow the Food/Beverage segment to be processed."""
        return segment_code == FOOD_SEGMENT_CODE
    
    def on_family_processed(self, family_code, family_desc, segment_code, is_new):
        if segment_code == FOOD_SEGMENT_CODE:
            self.stats['families'] += 1
            logging.info(f"Processing Food Family: {family_desc} ({family_code})")
    
    def on_class_processed(self, class_code, class_desc, family_code, is_new):
        self.stats['classes'] += 1
    
    def on_brick_processed(self, brick_code, brick_desc, class_code, is_new):
        self.stats['bricks'] += 1
    
    def on_attribute_type_processed(self, att_type_code, att_type_text, brick_code, is_new):
        self.stats['attribute_types'] += 1
    
    def on_attribute_value_processed(self, att_value_code, att_value_text, att_type_code, is_new):
        self.stats['attribute_values'] += 1
    
    def on_processing_complete(self, counters):
        logging.info("=== Food Segment Import Statistics ===")
        logging.info(f"Families: {self.stats['families']}")
        logging.info(f"Classes: {self.stats['classes']}")
        logging.info(f"Bricks: {self.stats['bricks']}")
        logging.info(f"Attribute Types: {self.stats['attribute_types']}")
        logging.info(f"Attribute Values: {self.stats['attribute_values']}")


def filter_xml_for_food_segment(input_xml_path, output_xml_path):
    """
    Filter the XML file to include only the Food/Beverage segment.
    
    Args:
        input_xml_path: Path to the original XML file
        output_xml_path: Path to save the filtered XML file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Parse the XML file
        tree = ET.parse(input_xml_path)
        root = tree.getroot()
        
        # Find all segments
        segments = root.findall(".//segment")
        if not segments:
            logging.error("No segments found in the XML file")
            return False
        
        # Keep only the Food/Beverage segment
        segments_to_remove = []
        for segment in segments:
            if segment.get("code") != FOOD_SEGMENT_CODE:
                segments_to_remove.append(segment)
        
        # Remove non-food segments
        for segment in segments_to_remove:
            root.remove(segment)
        
        # Save the filtered XML
        tree.write(output_xml_path)
        logging.info(f"Filtered XML saved to {output_xml_path}")
        return True
    
    except Exception as e:
        logging.error(f"Error filtering XML: {e}")
        return False


def main():
    """Main function to demonstrate advanced import of Food/Beverage segment."""
    # Create a downloader instance
    downloader = GPCDownloader(download_dir=GPC_DOWNLOAD_DIR)
    
    # Find or download the latest XML file
    xml_file = downloader.find_latest_xml_file()
    if not xml_file:
        logging.info("No cached XML files found. Downloading latest...")
        xml_file = downloader.download_latest_gpc_xml()
        if not xml_file:
            logging.error("Failed to download GPC data")
            return
    
    # Create a filtered XML file with only the Food/Beverage segment
    filtered_xml_path = os.path.join(os.path.dirname(xml_file), "food_segment.xml")
    if not filter_xml_for_food_segment(xml_file, filtered_xml_path):
        logging.error("Failed to filter XML for Food/Beverage segment")
        return
    
    # Create database connection
    db_connection = DatabaseConnection(DB_FILE)
    
    # Setup database
    if not setup_database(db_connection):
        logging.error("Failed to setup database")
        return
    
    # Create callback filter
    food_filter = FoodSegmentFilter()
    
    # Create parser and process filtered XML file
    parser = GPCParser(db_connection, callback=food_filter)
    parser.process_xml(filtered_xml_path)
    
    # Close database connection
    db_connection.close()
    
    logging.info("Food/Beverage segment import completed successfully")


if __name__ == "__main__":
    main()
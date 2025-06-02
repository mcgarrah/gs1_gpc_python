#!/usr/bin/env python3
"""
Example script demonstrating basic usage of the gs1_gpc package.
"""

import os
import logging
from gs1_gpc.db import DatabaseConnection, setup_database
from gs1_gpc.parser import GPCParser
from gs1_gpc.downloader import GPCDownloader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Get script directory
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define paths
GPC_DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, 'imports')
DB_FILE = os.path.join(SCRIPT_DIR, 'instances', 'example_import.sqlite3')

def main():
    """Main function to demonstrate basic import."""
    # Create a downloader instance
    downloader = GPCDownloader(download_dir=GPC_DOWNLOAD_DIR)
    
    # Find the latest XML file
    xml_file = downloader.find_latest_xml_file()
    if not xml_file:
        logging.error("No XML files found in %s", GPC_DOWNLOAD_DIR)
        return
    
    # Create database connection
    db_connection = DatabaseConnection(DB_FILE)
    
    # Setup database
    if not setup_database(db_connection):
        logging.error("Failed to setup database")
        return
    
    # Create parser and process XML file
    parser = GPCParser(db_connection)
    parser.process_xml(xml_file)
    
    # Close database connection
    db_connection.close()
    
    logging.info("Import completed successfully")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Example script demonstrating basic usage of the gs1_gpc package.
"""

import os
import logging
from gs1_gpc.db import DatabaseConnection, setup_database
from gs1_gpc.parser import process_gpc_xml
from gs1_gpc.downloader import find_latest_xml_file

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
    # Find the latest XML file
    xml_file = find_latest_xml_file(GPC_DOWNLOAD_DIR)
    if not xml_file:
        logging.error("No XML files found in %s", GPC_DOWNLOAD_DIR)
        return
    
    # Create database connection
    db_connection = DatabaseConnection(DB_FILE)
    
    # Setup database
    if not setup_database(db_connection):
        logging.error("Failed to setup database")
        return
    
    # Process XML file
    process_gpc_xml(xml_file, db_connection)
    
    # Close database connection
    db_connection.close()
    
    logging.info("Import completed successfully")

if __name__ == "__main__":
    main()
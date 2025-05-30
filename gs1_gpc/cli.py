#!/usr/bin/env python3
"""
Command line interface for GS1 GPC.
"""

import os
import sys
import logging
from datetime import datetime
import click
from pathlib import Path

from . import __version__
from .db import DatabaseConnection, setup_database
from .parser import process_gpc_xml
from .downloader import download_latest_gpc_xml, find_latest_xml_file
from .exporter import dump_database_to_sql

# Default paths
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_FILE = os.path.join(SCRIPT_DIR, 'data', 'instances', 'gpc_data_xml.sqlite3')
GPC_DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, 'data', 'imports')
DEFAULT_FALLBACK_XML_FILE = os.path.join(GPC_DOWNLOAD_DIR, 'en-v20241202.xml')


@click.group()
@click.version_option(version=__version__)
def cli():
    """GS1 GPC Command Line Tool"""
    pass


@cli.command()
@click.option('--xml-file', help='Path to the input GS1 GPC XML file')
@click.option('--db-file', default=DEFAULT_DB_FILE, 
              help='Path to the output database file')
@click.option('--db-type', default='sqlite', type=click.Choice(['sqlite', 'postgresql']),
              help='Database type (sqlite or postgresql)')
@click.option('--download', is_flag=True, help='Download the latest GPC data before import')
@click.option('--language', default='en', help='Language code for GPC data download (default: en)')
@click.option('--dump-sql', is_flag=True, help='Dump database tables to SQL file after import')
@click.option('--verbose', '-v', is_flag=True, help='Enable detailed debug logging')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all logging except errors')
def import_gpc(xml_file, db_file, db_type, download, language, dump_sql, verbose, quiet):
    """Import GS1 GPC data into a database"""
    # Configure logging
    if quiet:
        log_level = logging.ERROR
    elif verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
        
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Record start time
    start_time = datetime.now()
    logging.info("Import started at: %s", start_time.strftime('%Y-%m-%d %H:%M:%S'))
    
    # Determine which XML file to use
    if xml_file:
        # User explicitly specified an XML file
        xml_file_path = xml_file
        logging.info("Using user-specified XML file: %s", xml_file_path)
    elif download:
        # User wants to download the latest data
        logging.info("Download flag set. Attempting to download latest GPC data in language '%s'...", language)
        xml_file_path = download_latest_gpc_xml(language)
    else:
        # Find the latest cached XML file
        logging.info("Looking for latest cached XML file for language '%s'...", language)
        xml_file_path = find_latest_xml_file(GPC_DOWNLOAD_DIR, language)
        if not xml_file_path:
            logging.warning("No cached XML files found. Using fallback file.")
            xml_file_path = DEFAULT_FALLBACK_XML_FILE
    
    # Check if XML file exists
    if not os.path.exists(xml_file_path):
        logging.error("XML file not found: %s", xml_file_path)
        sys.exit(1)
    
    # Create database connection
    db_connection = DatabaseConnection(db_file, db_type)
    
    # Setup database
    if not setup_database(db_connection):
        logging.error("Failed to setup database. Exiting.")
        sys.exit(1)
    
    # Process XML file
    counters = process_gpc_xml(xml_file_path, db_connection)
    
    # Close database connection
    db_connection.close()
    
    # Dump database to SQL if requested
    if dump_sql and db_type == 'sqlite':
        logging.info("Dump SQL flag set. Dumping database to SQL file...")
        sql_file_path = dump_database_to_sql(db_file, language)
        if sql_file_path:
            logging.info("Database dumped to SQL file: %s", sql_file_path)
        else:
            logging.error("Failed to dump database to SQL file")
    elif dump_sql and db_type != 'sqlite':
        logging.error("SQL dump is only supported for SQLite databases")
    
    # Record end time and duration
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info("Import finished at: %s", end_time.strftime('%Y-%m-%d %H:%M:%S'))
    logging.info("Total execution time: %s", duration)


@cli.command()
@click.option('--db-file', default=DEFAULT_DB_FILE, help='Path to the SQLite database file')
@click.option('--language', default='en', help='Language code for the SQL filename')
def export_sql(db_file, language):
    """Export database tables to SQL file"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Check if database file exists
    if not os.path.exists(db_file):
        logging.error("Database file not found: %s", db_file)
        sys.exit(1)
    
    # Export database to SQL
    sql_file_path = dump_database_to_sql(db_file, language)
    if sql_file_path:
        logging.info("Database dumped to SQL file: %s", sql_file_path)
    else:
        logging.error("Failed to dump database to SQL file")
        sys.exit(1)


if __name__ == '__main__':
    cli()
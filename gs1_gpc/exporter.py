"""
SQL export functionality for GS1 GPC.

This module provides functions for exporting database tables to SQL files.
"""

import os
import logging
import sqlite3
from datetime import datetime

# Default export directory
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GPC_EXPORT_DIR = os.path.join(SCRIPT_DIR, 'data', 'exports')


def dump_database_to_sql(db_file_path, language_code="en"):
    """
    Dump all GPC tables from the SQLite database to a SQL file.
    
    Args:
        db_file_path (str): Path to the SQLite database file
        language_code (str): Language code to use in the filename
        
    Returns:
        str: Path to the SQL dump file or None if failed
    """
    try:
        # Ensure export directory exists
        os.makedirs(GPC_EXPORT_DIR, exist_ok=True)
        
        # Create SQL dump file path
        current_date = datetime.now().strftime("%Y%m%d")
        sql_filename = f"{language_code}-v{current_date}.sql"
        sql_file_path = os.path.join(GPC_EXPORT_DIR, sql_filename)
        
        # Connect to the database
        conn = sqlite3.connect(db_file_path)
        
        # Create a temporary in-memory database with only the gpc_ tables
        temp_conn = sqlite3.connect(":memory:")
        
        # Get list of all gpc_ tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'gpc_%';")
        tables = [table[0] for table in cursor.fetchall()]
        
        if not tables:
            logging.warning("No GPC tables found in the database")
            return None
            
        # Copy each gpc_ table to the temporary database
        for table in tables:
            # Get the CREATE statement for the table
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}';")
            create_stmt = cursor.fetchone()[0]
            
            # Create the table in the temporary database
            temp_conn.execute(create_stmt)
            
            # Copy the data
            cursor.execute(f"SELECT * FROM {table};")
            rows = cursor.fetchall()
            
            if rows:
                # Get column names for the INSERT statement
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [col[1] for col in cursor.fetchall()]
                placeholders = ", ".join(["?" for _ in columns])
                
                # Insert the data into the temporary database
                temp_conn.executemany(
                    f"INSERT INTO {table} VALUES ({placeholders});", 
                    rows
                )
        
        temp_conn.commit()
        
        # Use iterdump() to generate the SQL dump
        with open(sql_file_path, 'w') as f:
            # Write header
            f.write("-- GPC Database Dump\n")
            f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- Source: {db_file_path}\n")
            f.write("-- Tables: " + ", ".join(tables) + "\n\n")
            
            # Write the SQL dump
            for line in temp_conn.iterdump():
                f.write(line + "\n")
        
        # Close connections
        temp_conn.close()
        conn.close()
        
        logging.info("Database successfully dumped to %s", sql_file_path)
        return sql_file_path
        
    except Exception as e:
        logging.error("Error dumping database to SQL: %s", e)
        return None
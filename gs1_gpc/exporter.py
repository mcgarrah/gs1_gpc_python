"""
SQL export functionality for GS1 GPC.

This module provides classes for exporting database tables to SQL files.

The main class is GPCExporter which handles exporting GPC data from a SQLite database
to SQL files. A legacy function is provided for backward compatibility but new code
should use the GPCExporter class.
"""

import os
import logging
import sqlite3
from datetime import datetime

# Default export directory
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GPC_EXPORT_DIR = os.path.join(SCRIPT_DIR, 'data', 'exports')


class GPCExporter:
    """
    Class for exporting GS1 GPC data from a database to SQL files.
    
    This class provides methods to export GPC data from a SQLite database to SQL files.
    It extracts only the GPC-related tables (those with names starting with 'gpc_')
    and creates a SQL dump file that can be used to recreate the database.
    """
    
    def __init__(self, export_dir=None, language_code="en"):
        """
        Initialize a GPCExporter.
        
        Args:
            export_dir (str, optional): Directory where SQL files will be saved.
                                       If None, uses the default GPC_EXPORT_DIR.
            language_code (str): Language code to use in filenames (default: 'en')
        """
        self.export_dir = export_dir if export_dir is not None else GPC_EXPORT_DIR
        self.language_code = language_code
    
    def dump_database_to_sql(self, db_file_path):
        """
        Dump all GPC tables from the SQLite database to a SQL file.
        
        This method extracts all tables with names starting with 'gpc_' from the
        specified SQLite database and creates a SQL dump file. The dump file includes
        both the table structure (CREATE statements) and the data (INSERT statements).
        
        The SQL file is saved in the export directory with the naming convention:
        {language_code}-v{date}.sql
        
        Args:
            db_file_path (str): Path to the SQLite database file
            
        Returns:
            str: Path to the SQL dump file or None if failed
        """
        try:
            # Ensure export directory exists
            os.makedirs(self.export_dir, exist_ok=True)
            
            # Create SQL dump file path
            current_date = datetime.now().strftime("%Y%m%d")
            sql_filename = f"{self.language_code}-v{current_date}.sql"
            sql_file_path = os.path.join(self.export_dir, sql_filename)
            
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


# Legacy function for backward compatibility
def dump_database_to_sql(db_file_path, language_code="en", export_dir=None):
    """
    Dump all GPC tables from the SQLite database to a SQL file.
    
    This is a legacy function maintained for backward compatibility.
    New code should use the GPCExporter class instead.
    
    Args:
        db_file_path (str): Path to the SQLite database file
        language_code (str): Language code to use in the filename
        export_dir (str, optional): Directory where SQL file will be saved
        
    Returns:
        str: Path to the SQL dump file or None if failed
    """
    exporter = GPCExporter(export_dir=export_dir, language_code=language_code)
    return exporter.dump_database_to_sql(db_file_path)
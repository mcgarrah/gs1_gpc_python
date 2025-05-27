"""
Database operations for GS1 GPC Import.

This module provides functions for setting up and interacting with the database,
including creating tables and inserting data.
"""

import os
import logging
import sqlite3
import importlib.util

class DatabaseConnection:
    """Database connection abstraction for SQLite and PostgreSQL."""
    
    def __init__(self, connection_string, db_type='sqlite'):
        """
        Initialize a database connection.
        
        Args:
            connection_string (str): Connection string or path to database file
            db_type (str): Database type ('sqlite' or 'postgresql')
        """
        self.connection_string = connection_string
        self.db_type = db_type.lower()
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """
        Connect to the database.
        
        Returns:
            tuple: (connection, cursor) or (None, None) on failure
        """
        try:
            if self.db_type == 'sqlite':
                # Check if directory exists, create if not
                db_dir = os.path.dirname(self.connection_string)
                if db_dir and not os.path.exists(db_dir):
                    logging.info("Creating directory for database: %s", db_dir)
                    os.makedirs(db_dir)
                
                self.conn = sqlite3.connect(self.connection_string)
                self.cursor = self.conn.cursor()
                
                # Enable Foreign Key support in SQLite
                self.cursor.execute("PRAGMA foreign_keys = ON;")
                
            elif self.db_type == 'postgresql':
                # Check if psycopg2 is installed
                if not importlib.util.find_spec("psycopg2"):
                    logging.error("psycopg2 is not installed. Install it with: pip install psycopg2-binary")
                    return None, None
                
                import psycopg2
                self.conn = psycopg2.connect(self.connection_string)
                self.cursor = self.conn.cursor()
                
            else:
                logging.error("Unsupported database type: %s", self.db_type)
                return None, None
                
            logging.info("Database connection successful.")
            return self.conn, self.cursor
            
        except Exception as e:
            logging.error("Database connection error: %s", e)
            return None, None
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")
    
    def commit(self):
        """Commit changes to the database."""
        if self.conn:
            self.conn.commit()
            logging.info("Database changes committed.")
    
    def rollback(self):
        """Rollback changes to the database."""
        if self.conn:
            self.conn.rollback()
            logging.info("Database changes rolled back.")


def setup_database(db_connection):
    """
    Create GPC tables if they don't exist.
    
    Args:
        db_connection (DatabaseConnection): Database connection object
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn, cursor = db_connection.connect()
    if not conn or not cursor:
        return False
        
    try:
        # Create tables with portable SQL syntax
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gpc_segments (
            segment_code TEXT PRIMARY KEY,
            description TEXT
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gpc_families (
            family_code TEXT PRIMARY KEY,
            description TEXT,
            segment_code TEXT,
            FOREIGN KEY (segment_code) REFERENCES gpc_segments (segment_code)
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gpc_classes (
            class_code TEXT PRIMARY KEY,
            description TEXT,
            family_code TEXT,
            FOREIGN KEY (family_code) REFERENCES gpc_families (family_code)
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gpc_bricks (
            brick_code TEXT PRIMARY KEY,
            description TEXT,
            class_code TEXT,
            FOREIGN KEY (class_code) REFERENCES gpc_classes (class_code)
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gpc_attribute_types (
            att_type_code TEXT PRIMARY KEY,
            att_type_text TEXT,
            brick_code TEXT,
            FOREIGN KEY (brick_code) REFERENCES gpc_bricks (brick_code)
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gpc_attribute_values (
            att_value_code TEXT PRIMARY KEY,
            att_value_text TEXT,
            att_type_code TEXT,
            FOREIGN KEY (att_type_code) REFERENCES gpc_attribute_types (att_type_code)
        );
        ''')
        
        logging.info("Tables checked/created successfully.")
        return True
        
    except Exception as e:
        logging.error("Database error during setup: %s", e)
        return False


def insert_segment(cursor, segment_code, description):
    """
    Insert a segment record.
    
    Args:
        cursor: Database cursor
        segment_code (str): Segment code
        description (str): Segment description
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO gpc_segments (segment_code, description)
        VALUES (?, ?);
        ''', (segment_code, description))
        return cursor.rowcount > 0
    except Exception as e:
        logging.error("Error inserting segment %s: %s", segment_code, e)
        return False


def insert_family(cursor, family_code, description, segment_code):
    """
    Insert a family record.
    
    Args:
        cursor: Database cursor
        family_code (str): Family code
        description (str): Family description
        segment_code (str): Segment code
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO gpc_families (family_code, description, segment_code)
        VALUES (?, ?, ?);
        ''', (family_code, description, segment_code))
        return cursor.rowcount > 0
    except Exception as e:
        logging.error("Error inserting family %s: %s", family_code, e)
        return False


def insert_class(cursor, class_code, description, family_code):
    """
    Insert a class record.
    
    Args:
        cursor: Database cursor
        class_code (str): Class code
        description (str): Class description
        family_code (str): Family code
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO gpc_classes (class_code, description, family_code)
        VALUES (?, ?, ?);
        ''', (class_code, description, family_code))
        return cursor.rowcount > 0
    except Exception as e:
        logging.error("Error inserting class %s: %s", class_code, e)
        return False


def insert_brick(cursor, brick_code, description, class_code):
    """
    Insert a brick record.
    
    Args:
        cursor: Database cursor
        brick_code (str): Brick code
        description (str): Brick description
        class_code (str): Class code
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO gpc_bricks (brick_code, description, class_code)
        VALUES (?, ?, ?);
        ''', (brick_code, description, class_code))
        return cursor.rowcount > 0
    except Exception as e:
        logging.error("Error inserting brick %s: %s", brick_code, e)
        return False


def insert_attribute_type(cursor, att_type_code, att_type_text, brick_code):
    """
    Insert an attribute type record.
    
    Args:
        cursor: Database cursor
        att_type_code (str): Attribute type code
        att_type_text (str): Attribute type description
        brick_code (str): Brick code
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO gpc_attribute_types (att_type_code, att_type_text, brick_code)
        VALUES (?, ?, ?);
        ''', (att_type_code, att_type_text, brick_code))
        return cursor.rowcount > 0
    except Exception as e:
        logging.error("Error inserting attribute type %s: %s", att_type_code, e)
        return False


def insert_attribute_value(cursor, att_value_code, att_value_text, att_type_code):
    """
    Insert an attribute value record.
    
    Args:
        cursor: Database cursor
        att_value_code (str): Attribute value code
        att_value_text (str): Attribute value description
        att_type_code (str): Attribute type code
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO gpc_attribute_values (att_value_code, att_value_text, att_type_code)
        VALUES (?, ?, ?);
        ''', (att_value_code, att_value_text, att_type_code))
        return cursor.rowcount > 0
    except Exception as e:
        logging.error("Error inserting attribute value %s: %s", att_value_code, e)
        return False
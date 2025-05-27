"""Tests for the db module."""

import os
import tempfile
import unittest
from gs1_gpc.db import DatabaseConnection, setup_database

class TestDatabaseConnection(unittest.TestCase):
    """Test the DatabaseConnection class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
        self.temp_db.close()
        
    def tearDown(self):
        """Tear down test fixtures."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_sqlite_connection(self):
        """Test SQLite connection."""
        db_connection = DatabaseConnection(self.temp_db.name)
        conn, cursor = db_connection.connect()
        self.assertIsNotNone(conn)
        self.assertIsNotNone(cursor)
        db_connection.close()
    
    def test_setup_database(self):
        """Test database setup."""
        db_connection = DatabaseConnection(self.temp_db.name)
        result = setup_database(db_connection)
        self.assertTrue(result)
        
        # Check if tables were created
        conn, cursor = db_connection.connect()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'gpc_%';")
        tables = cursor.fetchall()
        self.assertEqual(len(tables), 6)  # 6 tables should be created
        db_connection.close()

if __name__ == '__main__':
    unittest.main()
Testing
=======

This document provides information about testing the GS1 GPC Import project.

Running Tests
-----------

We use pytest for testing. To run the tests:

.. code-block:: bash

   # Install development dependencies
   pip install -e ".[dev]"
   
   # Run tests
   pytest

To run tests with coverage:

.. code-block:: bash

   pytest --cov=gs1_gpc

To run a specific test:

.. code-block:: bash

   pytest gs1_gpc/tests/test_db.py

Writing Tests
-----------

Tests are located in the ``gs1_gpc/tests`` directory. Each module should have a corresponding test file.

Example test:

.. code-block:: python

   import unittest
   from gs1_gpc.db import DatabaseConnection

   class TestDatabaseConnection(unittest.TestCase):
       def test_sqlite_connection(self):
           db_connection = DatabaseConnection(':memory:')
           conn, cursor = db_connection.connect()
           self.assertIsNotNone(conn)
           self.assertIsNotNone(cursor)
           db_connection.close()

Test Data
--------

Test data is located in the ``gs1_gpc/tests/data`` directory. This includes sample XML files for testing the parser.

Continuous Integration
-------------------

We use GitHub Actions for continuous integration. The CI pipeline runs tests on multiple Python versions to ensure compatibility.

The CI configuration is located in the ``.github/workflows`` directory.
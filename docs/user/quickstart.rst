Quickstart
==========

Basic Usage
----------

After installing the package, you can use the ``gpc`` command-line tool to import GS1 GPC data into a database.

Basic Import
~~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc

This will:

1. Look for the latest cached XML file in the imports directory
2. If none found, use the fallback file
3. Import the data into the default SQLite database

Download Latest Data
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc --download

This will:

1. Download the latest GPC data from the GS1 API
2. Save it to the imports directory with standard naming convention: ``{language_code}-{version}.xml``
3. Import the data into the default SQLite database

Specify Language
~~~~~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc --download --language fr

This will download and import the French version of the GPC data.

Custom Files
~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc --xml-file ./my_custom_file.xml --db-file ./my_database.sqlite3

Export Database to SQL
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc --dump-sql

This will:

1. Import data as usual
2. Export all GPC tables to a SQL file in the exports directory
3. The SQL file will follow the naming convention: ``{language_code}-v{date}.sql``

Export Only (No Import)
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   gpc export-sql --db-file ./data/instances/gpc_data_xml.sqlite3

PostgreSQL Support
~~~~~~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc --db-type postgresql --db-file "postgresql://user:password@localhost/dbname"

Python API Usage
--------------

You can also use the package as a Python library:

.. code-block:: python

   from gs1_gpc.db import DatabaseConnection, setup_database
   from gs1_gpc.parser import process_gpc_xml
   from gs1_gpc.downloader import find_latest_xml_file

   # Find the latest XML file
   xml_file = find_latest_xml_file()
   
   # Create database connection
   db_connection = DatabaseConnection("my_database.sqlite3")
   
   # Setup database
   setup_database(db_connection)
   
   # Process XML file
   process_gpc_xml(xml_file, db_connection)
   
   # Close database connection
   db_connection.close()
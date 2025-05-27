Command Line Interface
====================

The ``gs1-gpc`` package provides a command-line interface (CLI) for importing GS1 GPC data into a database.

Commands
-------

import-gpc
~~~~~~~

Import GS1 GPC data into a database.

.. code-block:: bash

   gpc import-gpc [OPTIONS]

Options:

* ``--xml-file PATH``: Path to the input GS1 GPC XML file
* ``--db-file PATH``: Path to the output database file
* ``--db-type [sqlite|postgresql]``: Database type (default: sqlite)
* ``--download``: Download the latest GPC data before import
* ``--language TEXT``: Language code for GPC data download (default: en)
* ``--dump-sql``: Dump database tables to SQL file after import
* ``--verbose, -v``: Enable detailed debug logging
* ``--quiet, -q``: Suppress all logging except errors
* ``--help``: Show help message and exit

export-sql
~~~~~~~~

Export database tables to SQL file.

.. code-block:: bash

   gpc export-sql [OPTIONS]

Options:

* ``--db-file PATH``: Path to the SQLite database file
* ``--language TEXT``: Language code for the SQL filename (default: en)
* ``--help``: Show help message and exit

Examples
-------

Basic Import
~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc

Download Latest Data
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc --download

Specify Language
~~~~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc --download --language fr

Custom Files
~~~~~~~~~

.. code-block:: bash

   gpc import-gpc --xml-file ./my_custom_file.xml --db-file ./my_database.sqlite3

Export Database to SQL
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc --dump-sql

Export Only (No Import)
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   gpc export-sql --db-file ./data/instances/gpc_data_xml.sqlite3

PostgreSQL Support
~~~~~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc --db-type postgresql --db-file "postgresql://user:password@localhost/dbname"

Verbose Logging
~~~~~~~~~~~~

.. code-block:: bash

   gpc import-gpc --verbose
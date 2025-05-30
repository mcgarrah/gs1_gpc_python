GS1 GPC Import
=============

A tool for importing GS1 Global Product Classification (GPC) data into SQL databases.

.. image:: https://readthedocs.org/projects/gs1-gpc/badge/?version=latest
   :target: https://gs1-gpc.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/github/license/mcgarrah/gs1_gpc_import
   :target: https://github.com/mcgarrah/gs1_gpc_import/blob/main/LICENSE
   :alt: License

Key Features
-----------

* **Import GPC Data**: Import GS1 GPC XML data into SQLite or PostgreSQL databases
* **Download Latest Data**: Download the latest GPC data directly from GS1 API using the gpcc library
* **Automatic Fallback**: Use the newest cached version if download is not available
* **SQL Export**: Export database tables to SQL file for backup or migration
* **Database Portability**: Support for both SQLite and PostgreSQL
* **Command-line Interface**: Easy-to-use CLI with Click

Installation
-----------

Install from source:

.. code-block:: bash

   git clone https://github.com/mcgarrah/gs1_gpc_import.git
   cd gs1_gpc_import
   pip install -r requirements.txt
   pip install -e .

Quick Example
-----------

.. code-block:: bash

   # Import GPC data
   gpc import-gpc --download
   
   # Export to SQL
   gpc export-sql --db-file ./data/instances/gpc_data_xml.sqlite3

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user/installation
   user/quickstart
   user/cli
   user/database
   user/advanced_usage

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/cli
   api/db
   api/parser
   api/downloader
   api/exporter

.. toctree::
   :maxdepth: 1
   :caption: Development

   dev/contributing
   dev/testing
   dev/releasing

Indices and tables
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
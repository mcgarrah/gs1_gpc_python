Advanced Usage
=============

PostgreSQL Support
----------------

The GS1 GPC tool supports both SQLite and PostgreSQL databases. To use PostgreSQL, you need to install the PostgreSQL extra:

.. code-block:: bash

   pip install gs1_gpc[postgresql]

Then you can use the ``--db-type postgresql`` option with the ``gpc import-gpc`` command:

.. code-block:: bash

   gpc import-gpc --db-type postgresql --db-file "postgresql://user:password@localhost/dbname"

The connection string format is:

.. code-block:: text

   postgresql://username:password@hostname:port/database

Custom XML Files
--------------

You can use your own XML files instead of downloading them from the GS1 API:

.. code-block:: bash

   gpc import-gpc --xml-file ./my_custom_file.xml

The XML file must follow the GS1 GPC XML format with the following structure:

.. code-block:: xml

   <schema>
     <segment code="10000000" text="Segment Description">
       <family code="10100000" text="Family Description">
         <class code="10100100" text="Class Description">
           <brick code="10100101" text="Brick Description">
             <attType code="20000001" text="Attribute Type Description">
               <attValue code="30000001" text="Attribute Value Description" />
               <attValue code="30000002" text="Attribute Value Description" />
             </attType>
           </brick>
         </class>
       </family>
     </segment>
   </schema>

Logging
------

You can control the logging level with the ``--verbose`` and ``--quiet`` options:

.. code-block:: bash

   # Enable detailed debug logging
   gpc import-gpc --verbose
   
   # Suppress all logging except errors
   gpc import-gpc --quiet

Programmatic Usage
----------------

You can use the GS1 GPC tool as a Python library in your own code using the class-based API:

.. code-block:: python

   from gs1_gpc.db import DatabaseConnection, setup_database
   from gs1_gpc.parser import GPCParser
   from gs1_gpc.downloader import GPCDownloader
   from gs1_gpc.exporter import GPCExporter
   
   # Create a downloader instance
   downloader = GPCDownloader(download_dir="/path/to/downloads", language_code="en")
   
   # Download the latest GPC data
   xml_file = downloader.download_latest_gpc_xml()
   
   # Create database connection
   db_connection = DatabaseConnection('my_database.sqlite3')
   
   # Setup database
   setup_database(db_connection)
   
   # Create parser and process XML file
   parser = GPCParser(db_connection)
   parser.process_xml(xml_file)
   
   # Close database connection
   db_connection.close()
   
   # Export database to SQL
   exporter = GPCExporter(export_dir="/path/to/exports", language_code="en")
   exporter.dump_database_to_sql('my_database.sqlite3')

Using Models and Callbacks
------------------------

You can use the models and callbacks to process GPC data in a more structured way:

.. code-block:: python

   from gs1_gpc.db import DatabaseConnection, setup_database
   from gs1_gpc.parser import GPCParser
   from gs1_gpc.models import GPCModels
   from gs1_gpc.callbacks import GPCProcessedCallback
   
   # Custom callback implementation
   class MyCallback(GPCProcessedCallback):
       def on_brick_processed(self, brick_code, brick_desc, class_code, is_new):
           print(f"Processed brick: {brick_code} - {brick_desc}")
       
       def on_processing_complete(self, counters):
           print(f"Processing complete. Processed {counters['bricks_processed']} bricks.")
   
   # Create database connection
   db_connection = DatabaseConnection('my_database.sqlite3')
   setup_database(db_connection)
   
   # Create parser with callback and process XML file
   callback = MyCallback()
   parser = GPCParser(db_connection, callback=callback)
   parser.process_xml('gpc_data.xml')

Food Segment Example
------------------

The package includes an advanced example that demonstrates how to import only the Food/Beverage segment:

.. literalinclude:: ../../examples/food_segment_import.py
   :language: python
   :linenos:
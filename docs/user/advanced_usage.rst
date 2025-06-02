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

You can use the GS1 GPC tool as a Python library in your own code:

.. code-block:: python

   from gs1_gpc.db import DatabaseConnection, setup_database
   from gs1_gpc.parser import process_gpc_xml
   from gs1_gpc.downloader import download_latest_gpc_xml
   from gs1_gpc.exporter import dump_database_to_sql
   
   # Download the latest GPC data
   xml_file = download_latest_gpc_xml(language='en')
   
   # Create database connection
   db_connection = DatabaseConnection('my_database.sqlite3')
   
   # Setup database
   setup_database(db_connection)
   
   # Process XML file
   process_gpc_xml(xml_file, db_connection)
   
   # Close database connection
   db_connection.close()
   
   # Export database to SQL
   dump_database_to_sql('my_database.sqlite3', language='en')

Using Models and Callbacks
------------------------

You can use the models and callbacks to process GPC data in a more structured way:

.. code-block:: python

   from gs1_gpc.db import DatabaseConnection, setup_database
   from gs1_gpc.parser import process_gpc_xml
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
   
   # Process XML file with callback
   callback = MyCallback()
   process_gpc_xml('gpc_data.xml', db_connection, callback)
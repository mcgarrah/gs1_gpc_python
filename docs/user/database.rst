Database Schema
==============

The GS1 GPC Import tool creates a database with the following schema. All tables are prefixed with "gpc_" to avoid conflicts with other tables in the database.

Tables
-----

gpc_segments
~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE gpc_segments (
       segment_code TEXT PRIMARY KEY,
       description TEXT
   );

gpc_families
~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE gpc_families (
       family_code TEXT PRIMARY KEY,
       description TEXT,
       segment_code TEXT,
       FOREIGN KEY (segment_code) REFERENCES gpc_segments (segment_code)
   );

gpc_classes
~~~~~~~~~

.. code-block:: sql

   CREATE TABLE gpc_classes (
       class_code TEXT PRIMARY KEY,
       description TEXT,
       family_code TEXT,
       FOREIGN KEY (family_code) REFERENCES gpc_families (family_code)
   );

gpc_bricks
~~~~~~~~

.. code-block:: sql

   CREATE TABLE gpc_bricks (
       brick_code TEXT PRIMARY KEY,
       description TEXT,
       class_code TEXT,
       FOREIGN KEY (class_code) REFERENCES gpc_classes (class_code)
   );

gpc_attribute_types
~~~~~~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE gpc_attribute_types (
       att_type_code TEXT PRIMARY KEY,
       att_type_text TEXT,
       brick_code TEXT,
       FOREIGN KEY (brick_code) REFERENCES gpc_bricks (brick_code)
   );

gpc_attribute_values
~~~~~~~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE gpc_attribute_values (
       att_value_code TEXT PRIMARY KEY,
       att_value_text TEXT,
       att_type_code TEXT,
       FOREIGN KEY (att_type_code) REFERENCES gpc_attribute_types (att_type_code)
   );

Example Queries
-------------

List all segments and families
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   SELECT 
       gpc_segments.segment_code, 
       gpc_families.family_code, 
       gpc_segments.description AS segment_text, 
       gpc_families.description AS family_text 
   FROM gpc_segments 
   JOIN gpc_families ON gpc_segments.segment_code = gpc_families.segment_code;

List all hierarchy levels with limit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   SELECT 
       gpc_segments.segment_code, 
       gpc_families.family_code, 
       gpc_classes.class_code, 
       gpc_bricks.brick_code,
       gpc_segments.description AS segment_text, 
       gpc_families.description AS family_text, 
       gpc_classes.description AS class_text, 
       gpc_bricks.description AS brick_text
   FROM gpc_segments 
   JOIN gpc_families ON gpc_segments.segment_code = gpc_families.segment_code
   JOIN gpc_classes ON gpc_families.family_code = gpc_classes.family_code
   JOIN gpc_bricks ON gpc_classes.class_code = gpc_bricks.class_code
   LIMIT 16;

Filter by segment
~~~~~~~~~~~~~~

.. code-block:: sql

   SELECT 
       gpc_segments.segment_code, 
       gpc_families.family_code, 
       gpc_classes.class_code, 
       gpc_bricks.brick_code,
       gpc_segments.description AS segment_text, 
       gpc_families.description AS family_text, 
       gpc_classes.description AS class_text, 
       gpc_bricks.description AS brick_text
   FROM gpc_segments 
   JOIN gpc_families ON gpc_segments.segment_code = gpc_families.segment_code
   JOIN gpc_classes ON gpc_families.family_code = gpc_classes.family_code
   JOIN gpc_bricks ON gpc_classes.class_code = gpc_bricks.class_code
   WHERE gpc_segments.segment_code = '50000000' 
   LIMIT 16;
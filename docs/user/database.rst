Database Schema
==============

The GS1 GPC tool creates a database with the following schema. All tables are prefixed with "gpc_" to avoid conflicts with other tables in the database.

The core hierarchy uses 1:N foreign keys (segments → families → classes → bricks).
Attribute types and attribute values are global entities shared across bricks, so
their relationships are stored in junction tables to preserve the many-to-many
mappings from the GS1 XML.

.. note::

   **Changed in v1.0.0**: The ``gpc_attribute_types`` table no longer has a
   ``brick_code`` column and ``gpc_attribute_values`` no longer has an
   ``att_type_code`` column. These many-to-many relationships are now stored
   in the ``gpc_brick_attribute_types`` and ``gpc_attribute_type_values``
   junction tables. See the :doc:`CHANGELOG </changelog>` for migration details.

Core Hierarchy Tables
--------------------

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

Attribute Tables
---------------

gpc_attribute_types
~~~~~~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE gpc_attribute_types (
       att_type_code TEXT PRIMARY KEY,
       att_type_text TEXT
   );

gpc_attribute_values
~~~~~~~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE gpc_attribute_values (
       att_value_code TEXT PRIMARY KEY,
       att_value_text TEXT
   );

Junction Tables
--------------

These tables preserve the many-to-many relationships from the GS1 XML. The same
attribute type can appear on many bricks, and the same attribute value can appear
under many attribute types.

gpc_brick_attribute_types
~~~~~~~~~~~~~~~~~~~~~~

Links bricks to their attribute types.

.. code-block:: sql

   CREATE TABLE gpc_brick_attribute_types (
       brick_code TEXT NOT NULL,
       att_type_code TEXT NOT NULL,
       PRIMARY KEY (brick_code, att_type_code),
       FOREIGN KEY (brick_code) REFERENCES gpc_bricks (brick_code),
       FOREIGN KEY (att_type_code) REFERENCES gpc_attribute_types (att_type_code)
   );

gpc_attribute_type_values
~~~~~~~~~~~~~~~~~~~~~~

Links attribute types to their allowed values.

.. code-block:: sql

   CREATE TABLE gpc_attribute_type_values (
       att_type_code TEXT NOT NULL,
       att_value_code TEXT NOT NULL,
       PRIMARY KEY (att_type_code, att_value_code),
       FOREIGN KEY (att_type_code) REFERENCES gpc_attribute_types (att_type_code),
       FOREIGN KEY (att_value_code) REFERENCES gpc_attribute_values (att_value_code)
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

Get all attribute types for a brick
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Uses the ``gpc_brick_attribute_types`` junction table:

.. code-block:: sql

   SELECT at.att_type_code, at.att_type_text
   FROM gpc_brick_attribute_types bat
   JOIN gpc_attribute_types at ON bat.att_type_code = at.att_type_code
   WHERE bat.brick_code = '10000309'
   ORDER BY at.att_type_code;

Get all attribute values for an attribute type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Uses the ``gpc_attribute_type_values`` junction table:

.. code-block:: sql

   SELECT av.att_value_code, av.att_value_text
   FROM gpc_attribute_type_values atv
   JOIN gpc_attribute_values av ON atv.att_value_code = av.att_value_code
   WHERE atv.att_type_code = '20000001'
   ORDER BY av.att_value_code;

Find all bricks that share a given attribute type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   SELECT b.brick_code, b.description
   FROM gpc_brick_attribute_types bat
   JOIN gpc_bricks b ON bat.brick_code = b.brick_code
   WHERE bat.att_type_code = '20000142'
   ORDER BY b.brick_code;

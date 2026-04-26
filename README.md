# GS1 GPC

A tool for importing GS1 Global Product Classification (GPC) data into SQL databases.

## Features

- Import GS1 GPC XML data into SQLite or PostgreSQL databases
- Download the latest GPC data directly from GS1 API using the gpcc library
- Automatically use the newest cached version if download is not available
- Export database tables to SQL file for backup or migration
- Path handling relative to script location for reliable execution from any directory
- Command-line interface with Click
- Pip installable package

## Installation


### Development Installation

```bash
# Clone the repository
git clone https://github.com/mcgarrah/gs1_gpc_python.git
cd gs1_gpc_python

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Using requirements.txt

For convenience, you can install all dependencies including gpcc from GitHub:

```bash
pip install -r requirements.txt
pip install -e .
```

### PostgreSQL Support

To use PostgreSQL instead of SQLite, install the PostgreSQL extra:

```bash
pip install -e ".[postgresql]"
```

## Directory Structure

- `/data/imports` - Directory for XML files (downloaded or manually placed)
- `/data/instances` - Directory for SQLite database files
- `/data/exports` - Directory for SQL dump files

## Usage

### Basic Import

```bash
gpc import-gpc
```

This will:

1. Look for the latest cached XML file in the imports directory
2. If none found, use the fallback file
3. Import the data into the default SQLite database

### Download Latest Data

```bash
gpc import-gpc --download
```

This will:

1. Download the latest GPC data from the GS1 API
2. Save it to the imports directory with standard naming convention: `{language_code}-{version}.xml`
3. Import the data into the default SQLite database

### Specify Language

```bash
gpc import-gpc --download --language nl
```

This will download and import the Dutch version of the GPC data.

### Custom Files

```bash
gpc import-gpc --xml-file ./my_custom_file.xml --db-file ./my_database.sqlite3
```

### Export Database to SQL

```bash
gpc import-gpc --dump-sql
```

This will:

1. Import data as usual
2. Export all GPC tables to a SQL file in the exports directory
3. The SQL file will follow the naming convention: `{language_code}-v{date}.sql`

### Export Only (No Import)

```bash
gpc export-sql --db-file ./data/instances/gpc_data_xml.sqlite3
```

### PostgreSQL Support

```bash
gpc import-gpc --db-type postgresql --db-file "postgresql://user:password@localhost/dbname"
```

### Other Options

```bash
gpc import-gpc --help
```

## Database Schema

The database uses the following schema with all tables prefixed with "gpc_".

The core hierarchy uses 1:N foreign keys (segments → families → classes → bricks).
Attribute types and attribute values are global entities shared across bricks, so
their relationships are stored in junction tables to preserve the many-to-many
mappings from the GS1 XML.

```sql
-- Core hierarchy
CREATE TABLE gpc_segments (
    segment_code TEXT PRIMARY KEY,
    description TEXT
);

CREATE TABLE gpc_families (
    family_code TEXT PRIMARY KEY,
    description TEXT,
    segment_code TEXT,
    FOREIGN KEY (segment_code) REFERENCES gpc_segments (segment_code)
);

CREATE TABLE gpc_classes (
    class_code TEXT PRIMARY KEY,
    description TEXT,
    family_code TEXT,
    FOREIGN KEY (family_code) REFERENCES gpc_families (family_code)
);

CREATE TABLE gpc_bricks (
    brick_code TEXT PRIMARY KEY,
    description TEXT,
    class_code TEXT,
    FOREIGN KEY (class_code) REFERENCES gpc_classes (class_code)
);

-- Attribute types and values (global, shared across bricks)
CREATE TABLE gpc_attribute_types (
    att_type_code TEXT PRIMARY KEY,
    att_type_text TEXT
);

CREATE TABLE gpc_attribute_values (
    att_value_code TEXT PRIMARY KEY,
    att_value_text TEXT
);

-- Junction tables (many-to-many relationships)
CREATE TABLE gpc_brick_attribute_types (
    brick_code TEXT NOT NULL,
    att_type_code TEXT NOT NULL,
    PRIMARY KEY (brick_code, att_type_code),
    FOREIGN KEY (brick_code) REFERENCES gpc_bricks (brick_code),
    FOREIGN KEY (att_type_code) REFERENCES gpc_attribute_types (att_type_code)
);

CREATE TABLE gpc_attribute_type_values (
    att_type_code TEXT NOT NULL,
    att_value_code TEXT NOT NULL,
    PRIMARY KEY (att_type_code, att_value_code),
    FOREIGN KEY (att_type_code) REFERENCES gpc_attribute_types (att_type_code),
    FOREIGN KEY (att_value_code) REFERENCES gpc_attribute_values (att_value_code)
);
```

## Example Queries

### List all segments and families

```sql
SELECT 
    gpc_segments.segment_code, 
    gpc_families.family_code, 
    gpc_segments.description AS segment_text, 
    gpc_families.description AS family_text 
FROM gpc_segments 
JOIN gpc_families ON gpc_segments.segment_code = gpc_families.segment_code;
```

### List all hierarchy levels with limit

```sql
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
```

### Filter by segment

```sql
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
```

### Get all attribute types for a brick (via junction table)

```sql
SELECT at.att_type_code, at.att_type_text
FROM gpc_brick_attribute_types bat
JOIN gpc_attribute_types at ON bat.att_type_code = at.att_type_code
WHERE bat.brick_code = '10000309'
ORDER BY at.att_type_code;
```

### Get all attribute values for an attribute type (via junction table)

```sql
SELECT av.att_value_code, av.att_value_text
FROM gpc_attribute_type_values atv
JOIN gpc_attribute_values av ON atv.att_value_code = av.att_value_code
WHERE atv.att_type_code = '20000001'
ORDER BY av.att_value_code;
```

### Find all bricks that share a given attribute type

```sql
SELECT b.brick_code, b.description
FROM gpc_brick_attribute_types bat
JOIN gpc_bricks b ON bat.brick_code = b.brick_code
WHERE bat.att_type_code = '20000142'
ORDER BY b.brick_code;
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest gs1_gpc/tests/
```

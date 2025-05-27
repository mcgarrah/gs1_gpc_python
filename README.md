# GS1 GPC Import

A tool for importing GS1 Global Product Classification (GPC) data into an SQLite database.

## Features

- Import GS1 GPC XML data into an SQLite database
- Download the latest GPC data directly from GS1 API using the gpcc library
- Automatically use the newest cached version if download is not available
- Export database tables to SQL file for backup or migration
- Path handling relative to script location for reliable execution from any directory

## Directory Structure

- `/imports` - Directory for XML files (downloaded or manually placed)
- `/instances` - Directory for SQLite database files
- `/exports` - Directory for SQL dump files

## Setting up the environment

### Virtual Environment

```console
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### SQLite Client

```console
sudo apt install sqlite3
sqlite3 ./instances/gpc_data_xml.sqlite3
> .help
> .schema gpc_segments
> .quit
```

## Usage

### Basic Import

```console
python3 gpc_import_xml.py
```

This will:
1. Look for the latest cached XML file in the imports directory
2. If none found, use the fallback file
3. Import the data into the default SQLite database

### Download Latest Data

```console
python3 gpc_import_xml.py --download
```

This will:
1. Download the latest GPC data from the GS1 API
2. Save it to the imports directory with standard naming convention: `{language_code}-{version}.xml`
3. Import the data into the default SQLite database

### Specify Language

```console
python3 gpc_import_xml.py --download --language fr
```

This will download and import the French version of the GPC data.

### Custom Files

```console
python3 gpc_import_xml.py --xml-file ./my_custom_file.xml --db-file ./my_database.sqlite3
```

### Export Database to SQL

```console
python3 gpc_import_xml.py --dump-sql
```

This will:
1. Import data as usual
2. Export all GPC tables to a SQL file in the exports directory
3. The SQL file will follow the naming convention: `{language_code}-v{date}.sql`

### Other Options

```console
python3 gpc_import_xml.py --help
```

## Database Schema

The database uses the following schema with all tables prefixed with "gpc_":

```sql
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

CREATE TABLE gpc_attribute_types (
    att_type_code TEXT PRIMARY KEY,
    att_type_text TEXT,
    brick_code TEXT,
    FOREIGN KEY (brick_code) REFERENCES gpc_bricks (brick_code)
);

CREATE TABLE gpc_attribute_values (
    att_value_code TEXT PRIMARY KEY,
    att_value_text TEXT,
    att_type_code TEXT,
    FOREIGN KEY (att_type_code) REFERENCES gpc_attribute_types (att_type_code)
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
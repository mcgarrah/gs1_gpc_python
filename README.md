# GS1 GPC Import

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

### Important: GPCC Module Requirement

**Before installing this package**, you must install the GPCC module from GitHub:

```bash
pip install git+https://github.com/mcgarrah/gpcc.git@v1.0.1
```

The GPCC module is currently available as a custom release on GitHub. There is an outstanding pull request to push these changes upstream, after which it will be available via standard pip installation.

### Development Installation

```bash
# Clone the repository
git clone https://github.com/mcgarrah/gs1_gpc_import.git
cd gs1_gpc_import

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the gpcc dependency from GitHub (required)
pip install git+https://github.com/mcgarrah/gpcc.git@v1.0.1

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
gpc import
```

This will:
1. Look for the latest cached XML file in the imports directory
2. If none found, use the fallback file
3. Import the data into the default SQLite database

### Download Latest Data

```bash
gpc import --download
```

This will:
1. Download the latest GPC data from the GS1 API
2. Save it to the imports directory with standard naming convention: `{language_code}-{version}.xml`
3. Import the data into the default SQLite database

### Specify Language

```bash
gpc import --download --language fr
```

This will download and import the French version of the GPC data.

### Custom Files

```bash
gpc import --xml-file ./my_custom_file.xml --db-file ./my_database.sqlite3
```

### Export Database to SQL

```bash
gpc import --dump-sql
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
gpc import --db-type postgresql --db-file "postgresql://user:password@localhost/dbname"
```

### Other Options

```bash
gpc import --help
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

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest gs1_gpc/tests/
```
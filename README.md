# JSON import

## Setting up the environment

### Virtual Environment

``` console
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### SQLite Client

``` console
sudo apt install sqlite3
sqlite3 ./gpc.db
> .help
> .schema category
> .quit
```

### Running importer

``` console
✗ python3 import.py
Data from gpc_data.json imported successfully into gpc.db
```

### Review data in SQLite3 database

``` console
sqlite> .databases
main: /home/mcgarrah/github/food_service_nutrition/tmp/gpc.db r/w
sqlite> .schema
CREATE TABLE segments (
                segmentCode TEXT PRIMARY KEY,
                segmentDescription TEXT
            );
CREATE TABLE families (
                familyCode TEXT PRIMARY KEY,
                familyDescription TEXT,
                segmentCode TEXT,
                FOREIGN KEY (segmentCode) REFERENCES segments (segmentCode)
            );
CREATE TABLE classes (
                classCode TEXT PRIMARY KEY,
                classDescription TEXT,
                familyCode TEXT,
                FOREIGN KEY (familyCode) REFERENCES families (familyCode)
            );
CREATE TABLE bricks (
                brickCode TEXT PRIMARY KEY,
                brickDescription TEXT,
                classCode TEXT,
                FOREIGN KEY (classCode) REFERENCES classes (classCode)
            );
sqlite> .tables
bricks    classes   families  segments
```

## Data sources

### Products

* GS1 GCP GTIN for product lookups
  * [GPC browser allows you to browse all components (Segment, Family, Class, Brick and Attribute) of the current GPC schema](https://gpc-browser.gs1.org/)
  * [Python library and CLI tool to fetch information from GCP Browser](https://github.com/orsinium-labs/gpcc)
  * [A Python library and CLI for parsing and validating GTINs ("Global Trade Item Numbers"—also known as UPC/EAN/JAN/ISBN](https://github.com/enorganic/gtin)
  * [GS1_DigitalLink_Resolver_CE](https://github.com/gs1/GS1_DigitalLink_Resolver_CE)
  * https://www.gs1us.org/tools/gs1-us-data-hub/gs1-us-apis

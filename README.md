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

From JSON Importer attempt

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

XML Importer code

``` console
sqlite> .database
main: /home/mcgarrah/github/gs1_gpc_import/instances/gpc_data_xml.db r/w
sqlite> .tables
Bricks    Classes   Families  Segments

sqlite> .schema
CREATE TABLE Segments (
            segment_code TEXT PRIMARY KEY,
            description TEXT
        );
CREATE TABLE Families (
            family_code TEXT PRIMARY KEY,
            description TEXT,
            segment_code TEXT,
            FOREIGN KEY (segment_code) REFERENCES Segments (segment_code)
        );
CREATE TABLE Classes (
            class_code TEXT PRIMARY KEY,
            description TEXT,
            family_code TEXT,
            FOREIGN KEY (family_code) REFERENCES Families (family_code)
        );
CREATE TABLE Bricks (
            brick_code TEXT PRIMARY KEY,
            description TEXT,
            class_code TEXT,
            FOREIGN KEY (class_code) REFERENCES Classes (class_code)
        );

sqlite> SELECT Segments.segment_code AS segment_code, Families.family_code, Segments.description AS segment_text, Familie
s.description AS family_text FROM Segments JOIN Families ON Segments.segment_code = Families.segment_code;
50000000|50180000|Food/Beverage|Bread/Bakery Products
50000000|50220000|Food/Beverage|Cereal/Grain/Pulse Products
50000000|50150000|Food/Beverage|Oils/Fats Edible
50000000|50190000|Food/Beverage|Prepared/Preserved Foods

sqlite> .header on
sqlite> SELECT Segments.segment_code AS segment_code, Families.family_code, Segments.description AS segment_text, Families.description AS family_text FROM Segments JOIN Families ON Segments.segment_code = Families.segment_code;
segment_code|family_code|segment_text|family_text
50000000|50180000|Food/Beverage|Bread/Bakery Products
50000000|50220000|Food/Beverage|Cereal/Grain/Pulse Products
50000000|50150000|Food/Beverage|Oils/Fats Edible
50000000|50190000|Food/Beverage|Prepared/Preserved Foods

sqlite> .mode column
sqlite> SELECT Segments.segment_code AS segment_code, Families.family_code, Segments.description AS segment_text, Families.description AS family_text FROM Segments JOIN Families ON Segments.segment_code = Families.segment_code;
segment_code  family_code  segment_text   family_text
------------  -----------  -------------  ---------------------------
50000000      50180000     Food/Beverage  Bread/Bakery Products
50000000      50220000     Food/Beverage  Cereal/Grain/Pulse Products
50000000      50150000     Food/Beverage  Oils/Fats Edible
50000000      50190000     Food/Beverage  Prepared/Preserved Foods

sqlite> .header on
sqlite> .mode column
sqlite> SELECT Segments.segment_code AS segment_code, Families.family_code, Classes.class_code, Bricks.brick_code,
               Segments.description AS segment_text, Families.description AS family_text, Classes.description AS class_text, Bricks.description AS brick_text
FROM Segments JOIN Families ON Segments.segment_code = Families.segment_code
JOIN Classes ON Families.family_code = Classes.family_code
JOIN Bricks ON Classes.class_code = Bricks.class_code
LIMIT 16;
segment_code  family_code  class_code  brick_code  segment_text   family_text            class_text                     brick_text
------------  -----------  ----------  ----------  -------------  ---------------------  -----------------------------  -------------------------------------------
50000000      50180000     50181700    10000155    Food/Beverage  Bread/Bakery Products  Baking/Cooking Mixes/Supplies  Baking/Cooking Mixes (Frozen)
50000000      50180000     50181700    10000068    Food/Beverage  Bread/Bakery Products  Baking/Cooking Mixes/Supplies  Baking/Cooking Mixes (Perishable)
50000000      50180000     50181700    10000156    Food/Beverage  Bread/Bakery Products  Baking/Cooking Mixes/Supplies  Baking/Cooking Mixes (Shelf Stable)
50000000      50180000     50181700    10000595    Food/Beverage  Bread/Bakery Products  Baking/Cooking Mixes/Supplies  Baking/Cooking Mixes/Supplies Variety Packs
50000000      50180000     50181700    10000157    Food/Beverage  Bread/Bakery Products  Baking/Cooking Mixes/Supplies  Baking/Cooking Supplies (Frozen)
50000000      50180000     50181700    10000069    Food/Beverage  Bread/Bakery Products  Baking/Cooking Mixes/Supplies  Baking/Cooking Supplies (Perishable)
50000000      50180000     50181700    10000158    Food/Beverage  Bread/Bakery Products  Baking/Cooking Mixes/Supplies  Baking/Cooking Supplies (Shelf Stable)
50000000      50180000     50182100    10000304    Food/Beverage  Bread/Bakery Products  Biscuits/Cookies               Biscuits/Cookies (Frozen)
50000000      50180000     50182100    10000160    Food/Beverage  Bread/Bakery Products  Biscuits/Cookies               Biscuits/Cookies (Perishable)
50000000      50180000     50182100    10000161    Food/Beverage  Bread/Bakery Products  Biscuits/Cookies               Biscuits/Cookies (Shelf Stable)
50000000      50180000     50182100    10000596    Food/Beverage  Bread/Bakery Products  Biscuits/Cookies               Biscuits/Cookies Variety Packs
50000000      50180000     50182100    10000305    Food/Beverage  Bread/Bakery Products  Biscuits/Cookies               Dried Breads (Frozen)
50000000      50180000     50182100    10000166    Food/Beverage  Bread/Bakery Products  Biscuits/Cookies               Dried Breads (Shelf Stable)
50000000      50180000     50181900    10000163    Food/Beverage  Bread/Bakery Products  Bread                          Bread (Frozen)
50000000      50180000     50181900    10000164    Food/Beverage  Bread/Bakery Products  Bread                          Bread (Perishable)
50000000      50180000     50181900    10000165    Food/Beverage  Bread/Bakery Products  Bread                          Bread (Shelf Stable)

sqlite> SELECT Segments.segment_code AS segment_code, Families.family_code, Classes.class_code, Bricks.brick_code,
               Segments.description AS segment_text, Families.description AS family_text, Classes.description AS class_text, Bricks.description AS brick_text
FROM Segments JOIN Families ON Segments.segment_code = Families.segment_code
JOIN Classes ON Families.family_code = Classes.family_code
JOIN Bricks ON Classes.class_code = Bricks.class_code
WHERE Segments.segment_code = '50000000' LIMIT 16;

segment_code  family_code  class_code  brick_code  segment_text   family_text                     class_text                                               brick_text
------------  -----------  ----------  ----------  -------------  ------------------------------  -------------------------------------------------------  -----------------------------------------------
50000000      50410000     50410100    10008449    Food/Beverage  Animal-derived Edible Products  Animal-derived Edible Products - Prepared/Processed      Edible Bird Nest - Prepared/Processed
50000000      50410000     50410100    10008450    Food/Beverage  Animal-derived Edible Products  Animal-derived Edible Products - Prepared/Processed      Edible Donkey-hide Gelatin - Prepared/Processed
50000000      50410000     50410200    10008451    Food/Beverage  Animal-derived Edible Products  Animal-derived Edible Products - Unprepared/Unprocessed  Edible Bird Nest - Unprepared/Unprocessed
50000000      50200000     50202200    10008042    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Alcohol Flavouring Kit
50000000      50200000     50202200    10000142    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Alcohol Making Kits
50000000      50200000     50202200    10000143    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Alcohol Making Supplies
50000000      50200000     50202200    10000591    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Alcoholic Beverages Variety Packs
50000000      50200000     50202200    10000144    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Alcoholic Pre-mixed Drinks
50000000      50200000     50202200    10000589    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Alcoholic Syrups and Bitters
50000000      50200000     50202200    10000181    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Apple/Pear Alcoholic Beverage - Sparkling
50000000      50200000     50202200    10006327    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Apple/Pear Alcoholic Beverage - Still
50000000      50200000     50202200    10008032    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Apple/Pear Beverage - Sparkling (Non-Alcoholic)
50000000      50200000     50202200    10008033    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Apple/Pear Beverage - Still (Non-Alcoholic)
50000000      50200000     50202200    10000159    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Beer
50000000      50200000     50202200    10008029    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Beer (Non-Alcoholic)
50000000      50200000     50202200    10000227    Food/Beverage  Beverages                       Alcoholic Beverages (Includes De-Alcoholised Variants)   Liqueurs
```

## Data sources

### Products

* GS1 GCP GTIN for product lookups
  * [GPC browser allows you to browse all components (Segment, Family, Class, Brick and Attribute) of the current GPC schema](https://gpc-browser.gs1.org/)
  * [Python library and CLI tool to fetch information from GCP Browser](https://github.com/orsinium-labs/gpcc)
  * [A Python library and CLI for parsing and validating GTINs ("Global Trade Item Numbers"—also known as UPC/EAN/JAN/ISBN](https://github.com/enorganic/gtin)
  * [GS1_DigitalLink_Resolver_CE](https://github.com/gs1/GS1_DigitalLink_Resolver_CE)
  * https://www.gs1us.org/tools/gs1-us-data-hub/gs1-us-apis

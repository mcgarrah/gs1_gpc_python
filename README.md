# JSON import

Virtual Environment

``` console
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

SQLite Client

``` console
sudo apt install sqlite3
sqlite3 ./gpc.db
> .help
> .schema category
> .quit
```

``` console
✗ python3 import.py
Data from gpc_data.json imported successfully into gpc.db
```

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

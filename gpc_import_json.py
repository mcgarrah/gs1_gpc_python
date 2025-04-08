import json
import sqlite3

def import_gpc_to_sqlite(json_file, db_file, segment_filter=None):
    """
    Imports GS1 GPC data from a JSON file into an SQLite database, with optional segment filtering.

    Args:
        json_file (str): Path to the GS1 GPC JSON file.
        db_file (str): Path to the SQLite database file.
        segment_filter (str, optional): Segment code to filter by (e.g., '50000000'). Defaults to None.
    """

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Create tables (adjust schema as needed based on your GPC JSON structure)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS segments (
                segmentCode TEXT PRIMARY KEY,
                segmentDescription TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS families (
                familyCode TEXT PRIMARY KEY,
                familyDescription TEXT,
                segmentCode TEXT,
                FOREIGN KEY (segmentCode) REFERENCES segments (segmentCode)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                classCode TEXT PRIMARY KEY,
                classDescription TEXT,
                familyCode TEXT,
                FOREIGN KEY (familyCode) REFERENCES families (familyCode)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bricks (
                brickCode TEXT PRIMARY KEY,
                brickDescription TEXT,
                classCode TEXT,
                FOREIGN KEY (classCode) REFERENCES classes (classCode)
            )
        ''')

        # Insert data
        if 'segments' in data:
            for segment in data['segments']:
                cursor.execute('''
                    INSERT OR IGNORE INTO segments (segmentCode, segmentDescription)
                    VALUES (?, ?)
                ''', (segment['segmentCode'], segment['segmentDescription']))

        if 'families' in data:
            for family in data['families']:
                if segment_filter is None or family['segmentCode'] == segment_filter:
                    cursor.execute('''
                        INSERT OR IGNORE INTO families (familyCode, familyDescription, segmentCode)
                        VALUES (?, ?, ?)
                    ''', (family['familyCode'], family['familyDescription'], family['segmentCode']))

        if 'classes' in data:
            for class_data in data['classes']:
                family_code = class_data['familyCode']
                cursor.execute("SELECT segmentCode from families where familyCode=?",(family_code,))
                segment_code = cursor.fetchone()
                if segment_code is not None:
                    if segment_filter is None or segment_code[0] == segment_filter:
                        cursor.execute('''
                            INSERT OR IGNORE INTO classes (classCode, classDescription, familyCode)
                            VALUES (?, ?, ?)
                        ''', (class_data['classCode'], class_data['classDescription'], class_data['familyCode']))

        if 'bricks' in data:
            for brick in data['bricks']:
                class_code = brick['classCode']
                cursor.execute("SELECT familyCode from classes where classCode=?",(class_code,))
                family_code = cursor.fetchone()
                if family_code is not None:
                    cursor.execute("SELECT segmentCode from families where familyCode=?",(family_code[0],))
                    segment_code = cursor.fetchone()
                    if segment_code is not None:
                        if segment_filter is None or segment_code[0] == segment_filter:
                            cursor.execute('''
                                INSERT OR IGNORE INTO bricks (brickCode, brickDescription, classCode)
                                VALUES (?, ?, ?)
                            ''', (brick['brickCode'], brick['brickDescription'], brick['classCode']))

        conn.commit()
        conn.close()

        print(f"Data from {json_file} imported successfully into {db_file}")

    except FileNotFoundError:
        print(f"Error: File {json_file} not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file}.")
    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")
    except KeyError as e:
        print(f"KeyError: {e}. Check the JSON structure.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage:
json_file_path = './tmp/gpc_data.json'
db_file_path = './gpc.db'
segment_to_filter = '50000000'  # Filter for Food/Beverage

# Import all data
# import_gpc_to_sqlite(json_file_path, db_file_path)

# Import only Food/Beverage data
import_gpc_to_sqlite(json_file_path, db_file_path, segment_to_filter)

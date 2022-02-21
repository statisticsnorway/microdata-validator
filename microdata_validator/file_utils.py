import json
import logging
import sqlite3 as db

from pathlib import Path
from typing import Tuple
from jsonschema import validate

logger = logging.getLogger()


def load_json(filepath: Path) -> dict:
    try:
        with filepath.open() as json_file:
            return json.load(json_file)
    except Exception as e:
        logging.error(f"Failed to open file at {str(Path)}")
        logging.error(f"{str(e)}")


def write_json(filepath: Path, content: dict) -> None:
    with open(filepath, 'w') as json_file:
        json.dump(
            content, json_file, indent=4, ensure_ascii=False
        )


def validate_json_with_schema(json_file: Path) -> None:
    json_schema_file = Path(__file__).parent.joinpath(
        "DatasetMetadataSchema.json"
    )
    with open(json_schema_file, mode="r", encoding="utf-8") as schema:
        metadata_schema = json.load(schema)
    with open(json_file, mode="r", encoding="utf-8") as metadata:
        metadata_json = json.load(metadata)
    validate(
        instance=metadata_json,
        schema=metadata_schema
    )


def create_temp_sqlite_db_file(db_file: Path) -> Tuple[db.Connection, db.Cursor]:
    sql_create_table = """
        CREATE TABLE temp_dataset (
            row_number INT NOT NULL,
            unit_id TEXT NOT NULL, 
            value TEXT NOT NULL, 
            start TEXT, 
            stop TEXT, 
            attributes TEXT) """

    db_conn = db.connect(db_file)
    cursor = db_conn.cursor()
    cursor.execute(sql_create_table)
    # Set Sqlite-params to speed up performance
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("BEGIN TRANSACTION")
    return (db_conn, cursor)


def read_temp_sqlite_db_data_sorted(db_file: Path) -> Tuple[db.Connection, db.Cursor]:
    sql_select_sorted = """\
        SELECT row_number, unit_id, value, start, stop, attributes
        FROM temp_dataset
        ORDER BY unit_id, start, stop """

    db_conn = db.connect(db_file)
    cursor = db_conn.cursor()
    #cursor.execute("PRAGMA synchronous = OFF")
    #cursor.execute("BEGIN TRANSACTION")
    cursor.execute(sql_select_sorted)
    return (db_conn, cursor)

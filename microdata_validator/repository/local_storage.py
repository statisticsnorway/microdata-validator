import csv
import json
import logging
import sqlite3 as db
from pathlib import Path
from typing import Tuple


logger = logging.getLogger()


def load_json(filepath: Path) -> dict:
    try:
        with filepath.open() as json_file:
            return json.load(json_file)
    except Exception as e:
        logging.error(f"Failed to open file at {str(Path)}")
        raise e


def write_json(filepath: Path, content: dict) -> None:
    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(
            content, json_file, indent=4, ensure_ascii=False
        )


def _create_temp_sqlite_db_file(
    db_file: Path
) -> Tuple[db.Connection, db.Cursor]:
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


def insert_data_csv_into_sqlite(
    sqlite_file_path, dataset_data_file, field_separator=";"
) -> None:
    db_conn, cursor = _create_temp_sqlite_db_file(
        sqlite_file_path
    )
    with open(file=dataset_data_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=field_separator)
        cursor.executemany(
            "INSERT INTO temp_dataset "
            "(row_number, unit_id, value, start, stop, attributes) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            reader
        )
    db_conn.commit()
    db_conn.close()
    logger.debug(
        f'Done reading datafile "{dataset_data_file}" '
        'into temp Sqlite database table.'
    )


def read_temp_sqlite_db_data_sorted(
    db_file: Path
) -> Tuple[db.Connection, db.Cursor]:
    sql_select_sorted = """
        SELECT row_number, unit_id, value, start, stop, attributes
        FROM temp_dataset
        ORDER BY unit_id, start, stop
    """

    db_conn = db.connect(db_file)
    cursor = db_conn.cursor()
    # cursor.execute("PRAGMA synchronous = OFF")
    # cursor.execute("BEGIN TRANSACTION")
    cursor.execute(sql_select_sorted)
    return (db_conn, cursor)

import csv
import json
import logging
import os
import shutil
import sqlite3 as db
from pathlib import Path
from typing import Tuple, Union
import uuid


logger = logging.getLogger()


def load_json(filepath: Path) -> dict:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to open file at {str(Path)}")
        raise e


def write_json(filepath: Path, content: dict) -> None:
    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(
            content, json_file, indent=4, ensure_ascii=False
        )


def resolve_working_directory(
    working_directory: Union[str, None]
) -> Tuple[Path, bool]:
    """
    Generates a working directory if a working directory is not supplied.
    Returns a tuple with:
        * The working directory Path
        * True, if directory was generated. False if not.
    """
    if working_directory:
        return Path(working_directory), False
    else:
        generated_working_directory = Path(str(uuid.uuid4()))
        os.mkdir(generated_working_directory)
        return generated_working_directory, True


def clean_up_temporary_files(
    dataset_name: str,
    working_directory: Path,
    delete_working_directory: Path = False
):
    generated_files = [
        f'{dataset_name}.csv',
        f'{dataset_name}.json',
        f'{dataset_name}.db',
    ]
    if delete_working_directory:
        temporary_files = os.listdir(working_directory)
        unknown_files = [
            file for file in temporary_files if file not in generated_files
        ]
        if not unknown_files:
            try:
                shutil.rmtree(working_directory)
            except Exception as e:
                logger.error(
                    'An exception occured while attempting to delete'
                    f'temporary files: {e}'
                )
        else:
            for file in generated_files:
                try:
                    os.remove(working_directory / file)
                except FileNotFoundError:
                    logger.error(
                        f"Could not find file {file} in working directory "
                        "when attempting to delete temporary files."
                    )
    else:
        for file in generated_files:
            try:
                os.remove(working_directory / file)
            except FileNotFoundError:
                logger.error(
                    f"Could not find file {file} in working directory "
                    "when attempting to delete temporary files."
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

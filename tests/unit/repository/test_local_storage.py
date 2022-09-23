import csv
import os
from pathlib import Path

from microdata_validator.repository import local_storage

RESOURCE_DIR = Path('tests/resources/repository')
UNSORTED_DATASET_PATH = RESOURCE_DIR / 'unsorted_dataset.csv'
SORTED_DATASET_PATH = RESOURCE_DIR / 'sorted_dataset.csv'
SQLITE_FILE_PATH = RESOURCE_DIR / 'sql_dataset.db'


def test_sql_read_sorted():
    local_storage.insert_data_csv_into_sqlite(
        SQLITE_FILE_PATH, UNSORTED_DATASET_PATH
    )
    db_conn, db_cursor = local_storage.read_temp_sqlite_db_data_sorted(
        SQLITE_FILE_PATH
    )
    with open(
        file=SORTED_DATASET_PATH, newline='', encoding='utf-8'
    ) as f:
        reader = csv.reader(f, delimiter=';')
        expected_sorted = list(reader)
    sql_sorted = [
        [str(data_row[0])] + list(data_row[1:])
        for data_row in list(db_cursor)
    ]
    db_conn.close()
    assert sql_sorted == expected_sorted


def teardown_function():
    try:
        os.remove(SQLITE_FILE_PATH)
    except Exception:
        pass

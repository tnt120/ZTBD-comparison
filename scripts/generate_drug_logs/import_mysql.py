import mysql.connector
from tqdm import tqdm
from time import time
import argparse

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from common.utils import print_colored, get_colored, import_n_records
from generate_drug_logs.defaults import DEFAULT_RECORDS_COUNT, DEFAULT_FILE


def _parse_args():
    parser = argparse.ArgumentParser(description="Parameter logs import script options")

    parser.add_argument(
        "--records_num",
        type=int,
        default=DEFAULT_RECORDS_COUNT,
        help="number of records to import.",
    )

    return parser.parse_args()


def import_mysql_drug_logs(records_count, records=None):
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
    )
    cursor = conn.cursor()

    if records is None:
        records = import_n_records(DEFAULT_FILE, records_count)

    if records == False:
        print_colored("[MySQL] Can't continue", "RED")
        return

    print_colored(
        f'[MySQL] Inserting {get_colored(len(records), "WHITE", restore={"color":"BLUE"})} records',
        "BLUE",
    )

    start = time()
    batch = []

    sql = "INSERT INTO drugs_logs (id, created_at, day, taken_time, time, drug_id, user_id) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    for rec in tqdm(records, desc="Inserting"):
        batch.append(
            (
                rec["id"],
                rec["created_at"],
                rec["day"],
                rec["taken_time"],
                rec["time"],
                rec["drug_id"],
                rec["user_id"],
            )
        )
        if len(batch) >= 10000:
            cursor.executemany(sql, batch)
            conn.commit()
            batch = []
    if batch:
        cursor.executemany(sql, batch)
        conn.commit()
    end = time()
    cursor.close()
    conn.close()

    return end - start


if __name__ == "__main__":
    args = _parse_args()

    time_taken = import_mysql_drug_logs(args.records_num)

    if time_taken:
        print_colored("Insert complete", "GREEN")

        print_colored(f"Time taken: {time_taken}s")

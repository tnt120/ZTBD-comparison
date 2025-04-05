import mysql.connector
from datetime import datetime
from tqdm import tqdm
from time import time
from uuid import uuid4
import argparse

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from common.utils import print_colored, get_colored, import_n_records
from generate_user_drugs.defaults import DEFAULT_RECORDS_COUNT, DEFAULT_FILE


def _parse_args():
    parser = argparse.ArgumentParser(description="Parameter logs import script options")

    parser.add_argument(
        "--records_num",
        type=int,
        default=DEFAULT_RECORDS_COUNT,
        help="number of records to import.",
    )

    return parser.parse_args()


def import_mysql_user_drugs(records_count, records=None):
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
    sql = "INSERT INTO user_drugs (id, amount, dose_size, end_date, priority, start_date, drug_id, user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    for rec in tqdm(records, desc="Inserting"):
        batch.append(
            (
                rec["id"],
                rec["amount"],
                rec["dose_size"],
                datetime.fromisoformat(rec["end_date"]),
                rec["priority"],
                datetime.fromisoformat(rec["start_date"]),
                rec["drug_id"],
                rec["user_id"],
            )
        )
        if len(batch) >= 5000:
            cursor.executemany(sql, batch)
            conn.commit()
            batch = []
    if batch:
        cursor.executemany(sql, batch)
        conn.commit()

    batch_day = []
    for row in records:
        for day in row["days"]:
            batch_day.append((str(uuid4()), day.strip(), row["id"]))
            if len(batch_day) >= 5000:
                cursor.executemany(
                    "INSERT INTO drug_dose_day (id, day, user_drug_id) VALUES (%s, %s, %s)",
                    batch_day,
                )
                conn.commit()
                batch_day = []

    if batch_day:
        cursor.executemany(
            "INSERT INTO drug_dose_day (id, day, user_drug_id) VALUES (%s, %s, %s)",
            batch_day,
        )
        conn.commit()

    batch_time = []
    for row in records:
        for t in row["times"]:
            batch_time.append(
                (str(uuid4()), datetime.strptime(t, "%H:%M:%S").time(), row["id"])
            )
            if len(batch_time) >= 5000:
                cursor.executemany(
                    "INSERT INTO drug_dose_time (id, dose_time, user_drug_id) VALUES (%s, %s, %s)",
                    batch_time,
                )
                conn.commit()
                batch_time = []

    if batch_time:
        cursor.executemany(
            "INSERT INTO drug_dose_time (id, dose_time, user_drug_id) VALUES (%s, %s, %s)",
            batch_time,
        )
        conn.commit()
    end = time()
    cursor.close()
    conn.close()

    return end - start


if __name__ == "__main__":
    args = _parse_args()

    time_taken = import_mysql_user_drugs(args.records_num)

    if time_taken:
        print_colored("Insert complete", "GREEN")

        print_colored(f"Time taken: {time_taken}s")

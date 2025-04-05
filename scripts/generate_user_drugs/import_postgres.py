import psycopg2
from datetime import datetime
from tqdm import tqdm
from time import time
from uuid import uuid4
import argparse

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
)
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


def import_postgres_user_drugs(records_count, records=None):
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        port=POSTGRES_PORT,
    )
    cursor = conn.cursor()

    if records is None:
        records = import_n_records(DEFAULT_FILE, records_count)

    if records == False:
        print_colored("[PostgreSQL] Can't continue", "RED")
        return

    print_colored(
        f'[PostgreSQL] Inserting {get_colored(len(records), "WHITE", restore={"color":"BLUE"})} records',
        "BLUE",
    )

    start = time()
    batch = []
    for row in tqdm(records, desc="Inserting"):
        batch.append(
            (
                row["id"],
                row["amount"],
                row["dose_size"],
                datetime.fromisoformat(row["end_date"]),
                row["priority"],
                datetime.fromisoformat(row["start_date"]),
                row["drug_id"],
                row["user_id"],
            )
        )
    if len(batch) >= 5000:
        args_str = ",".join(
            cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s)", b).decode() for b in batch
        )
        cursor.execute(
            "INSERT INTO user_drugs (id, amount, dose_size, end_date, priority, start_date, drug_id, user_id) VALUES "
            + args_str
        )
        conn.commit()
        batch = []
    if batch:
        args_str = ",".join(
            cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s)", b).decode() for b in batch
        )
        cursor.execute(
            "INSERT INTO user_drugs (id, amount, dose_size, end_date, priority, start_date, drug_id, user_id) VALUES "
            + args_str
        )
        conn.commit()

    batch_day = []

    for row in records:
        for day in row["days"]:
            batch_day.append((str(uuid4()), day, row["id"]))
            if len(batch_day) >= 5000:
                args_str = ",".join(
                    cursor.mogrify("(%s,%s,%s)", b).decode() for b in batch_day
                )
                cursor.execute(
                    "INSERT INTO drug_dose_day (id, day, user_drug_id) VALUES "
                    + args_str
                )
                conn.commit()
                batch_day = []
    if batch_day:
        args_str = ",".join(cursor.mogrify("(%s,%s,%s)", b).decode() for b in batch_day)
        cursor.execute(
            "INSERT INTO drug_dose_day (id, day, user_drug_id) VALUES " + args_str
        )
        conn.commit()

    batch_time = []
    for row in records:
        for t in row["times"]:
            batch_time.append(
                (str(uuid4()), datetime.strptime(t, "%H:%M:%S").time(), row["id"])
            )
            if len(batch_time) >= 5000:
                args_str = ",".join(
                    cursor.mogrify("(%s,%s,%s)", b).decode() for b in batch_time
                )
                cursor.execute(
                    "INSERT INTO drug_dose_time (id, dose_time, user_drug_id) VALUES "
                    + args_str
                )
                conn.commit()
                batch_time = []
    if batch_time:
        args_str = ",".join(
            cursor.mogrify("(%s,%s,%s)", b).decode() for b in batch_time
        )
        cursor.execute(
            "INSERT INTO drug_dose_time (id, dose_time, user_drug_id) VALUES "
            + args_str
        )
        conn.commit()
    end = time()
    cursor.close()
    conn.close()

    return end - start


if __name__ == "__main__":
    args = _parse_args()

    time_taken = import_postgres_user_drugs(args.records_num)

    if time_taken:
        print_colored("Insert complete", "GREEN")

        print_colored(f"Time taken: {time_taken}s")

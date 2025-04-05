import psycopg2
from datetime import datetime
from tqdm import tqdm
from time import time
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
from generate_parameter_logs.defaults import DEFAULT_RECORDS_COUNT, DEFAULT_FILE


def _parse_args():
    parser = argparse.ArgumentParser(description="Parameter logs import script options")

    parser.add_argument(
        "--records_num",
        type=int,
        default=DEFAULT_RECORDS_COUNT,
        help="number of records to import.",
    )

    return parser.parse_args()


def import_postgres_parameters(records_count, records=None):
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
    for rec in tqdm(records, desc="Inserting"):
        batch.append(
            (
                rec["id"],
                datetime.fromisoformat(rec["created_at"]),
                rec["value"],
                rec["parameter_id"],
                rec["user_id"],
            )
        )
        if len(batch) >= 10000:
            args_str = ",".join(
                cursor.mogrify("(%s,%s,%s,%s,%s)", b).decode("utf-8") for b in batch
            )
            cursor.execute(
                "INSERT INTO parameters_logs (id, created_at, value, parameter_id, user_id) VALUES "
                + args_str
            )
            conn.commit()
            batch = []
    if batch:
        args_str = ",".join(
            cursor.mogrify("(%s,%s,%s,%s,%s)", b).decode("utf-8") for b in batch
        )
        cursor.execute(
            "INSERT INTO parameters_logs (id, created_at, value, parameter_id, user_id) VALUES "
            + args_str
        )
        conn.commit()
    end = time()
    cursor.close()
    conn.close()

    return end - start


if __name__ == "__main__":
    args = _parse_args()

    time_taken = import_postgres_parameters(args.records_num)

    if time_taken:
        print_colored("Insert complete", "GREEN")

        print_colored(f"Time taken: {time_taken}s")

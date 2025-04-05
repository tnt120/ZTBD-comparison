import psycopg2
import random
from datetime import datetime, timedelta, time as time_obj
from uuid import uuid4
from tqdm import tqdm
import json
import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from env import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
)
from common.utils import print_colored, random_datetime, get_colored
from generate_drug_logs.defaults import DEFAULT_RECORDS_COUNT, WEEKDAYS, DEFAULT_FILE


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Parameter logs generation script options"
    )

    parser.add_argument(
        "--records_num",
        type=int,
        default=DEFAULT_RECORDS_COUNT,
        help="number of records to generate. It's one time process, so can be high number",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_FILE,
        help="File name to write into.",
    )

    return parser.parse_args()


def generate(records_count, output_file=DEFAULT_FILE, skip_file_check=False):

    if not skip_file_check and os.path.exists(output_file):
        if input(f"Data is already generated. Regenerate? y/[n]: ").lower() != "y":
            print_colored("Generation skipped", "YELLOW")
            return

    pg_conn = psycopg2.connect(
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        port=POSTGRES_PORT,
    )
    pg_cursor = pg_conn.cursor()

    print_colored("Acquiring data from postgres...", "BLUE")

    pg_cursor.execute("SELECT user_id, drug_id FROM user_drugs")
    user_drugs = pg_cursor.fetchall()

    print_colored(f'User drugs: {get_colored(len(user_drugs), "WHITE")}', "YELLOW")

    if len(user_drugs) == 0:
        print_colored(
            "Can't proceed with missing data. Previous file untouched.", "RED"
        )
        return False

    records = []
    now = datetime.now()
    start_date = now - timedelta(days=180)

    print_colored(
        f"\nWill generate {get_colored(records_count, 'WHITE', restore={'color':'BLUE'})} records.",
        "BLUE",
    )

    for _ in tqdm(
        range(records_count),
        desc=get_colored("Generating data", "BLUE", style="BRIGHT"),
    ):
        user_id, drug_id = random.choice(user_drugs)
        created_at = random_datetime(start_date, now)
        day = WEEKDAYS[created_at.weekday()]
        planned_time = time_obj(random.randint(6, 22), random.choice([0, 15, 30, 45]))

        taken_time_dt = datetime.combine(created_at.date(), planned_time) + timedelta(
            minutes=random.randint(-10, 10)
        )
        taken_time = taken_time_dt.time()

        records.append(
            {
                "id": str(uuid4()),
                "created_at": created_at.isoformat(),
                "day": day,
                "taken_time": taken_time.isoformat(),
                "time": planned_time.isoformat(),
                "drug_id": drug_id,
                "user_id": user_id,
            }
        )

    print_colored(
        f'\nWriting to {get_colored(output_file, "WHITE", restore={"color": "BLUE"})} file.',
        "BLUE",
    )

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as file:
        json.dump(records, file, indent=4)

    print_colored("Generation process completed.", "GREEN")


if __name__ == "__main__":
    args = _parse_args()

    generate(args.records_num, args.output, True)

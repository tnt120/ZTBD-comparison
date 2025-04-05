import psycopg2
import random
from datetime import datetime, timedelta, time
from uuid import uuid4
from tqdm import tqdm
import json
import sys
import os
import argparse
from time import time as t_time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from env import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
)
from common.utils import print_colored, get_colored
from generate_user_drugs.defaults import (
    WEEKDAYS,
    MIN_USER_DRUGS,
    MAX_USER_DRUGS,
    DEFAULT_FILE,
)


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Parameter logs generation script options"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_FILE,
        help="File name to write into.",
    )

    return parser.parse_args()


def generate(output_file=DEFAULT_FILE, skip_file_check=False):

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

    pg_cursor.execute("SELECT id FROM users")
    user_ids = [row[0] for row in pg_cursor.fetchall()]

    pg_cursor.execute("SELECT id FROM drugs")
    drug_ids = pg_cursor.fetchall()

    print_colored(f'Users: {get_colored(len(user_ids), "WHITE")}', "YELLOW")

    print_colored(f'Drugs: {get_colored(len(drug_ids), "WHITE")}', "YELLOW")

    if len(user_ids) == 0 or len(drug_ids) == 0:
        print_colored(
            "Can't proceed with missing data. Previous file untouched.", "RED"
        )
        return False

    records = []
    now = datetime.now()
    start_date = now - timedelta(days=180)

    print_colored(
        f"\nWill generate between {get_colored(MIN_USER_DRUGS, 'WHITE', restore={'color':'BLUE'})} and {get_colored(MAX_USER_DRUGS, 'WHITE', restore={'color':'BLUE'})} user drug assignment records.",
        "BLUE",
    )

    for user_id in tqdm(
        user_ids, get_colored("Generating data", "BLUE", style="BRIGHT")
    ):
        selected = random.sample(
            drug_ids, random.randint(MIN_USER_DRUGS, MAX_USER_DRUGS)
        )
        for drug_id in selected:
            user_drug_id = str(uuid4())
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=random.randint(30, 180))
            dose_days = random.sample(WEEKDAYS, random.randint(1, 7))
            dose_times = [
                time(random.randint(6, 22), random.choice([0, 15, 30, 45])).isoformat()
                for _ in range(random.randint(1, 5))
            ]

            records.append(
                {
                    "id": user_drug_id,
                    "amount": random.randint(10, 100),
                    "dose_size": random.randint(1, 3),
                    "end_date": end_date.isoformat(),
                    "priority": random.choice(["LOW", "HIGH"]),
                    "start_date": start_date.isoformat(),
                    "drug_id": drug_id[0],
                    "user_id": user_id,
                    "days": dose_days,
                    "times": dose_times,
                }
            )
    random.shuffle(records)

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

    generate(args.output, True)

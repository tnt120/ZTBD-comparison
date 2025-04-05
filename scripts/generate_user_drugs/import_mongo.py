from pymongo import MongoClient, UpdateOne
from datetime import datetime
from tqdm import tqdm
from time import time
import argparse

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB

from common.utils import print_colored, get_colored, import_n_records
from generate_user_drugs.defaults import DEFAULT_RECORDS_COUNT, DEFAULT_FILE


def _parse_args():
    parser = argparse.ArgumentParser(description="Parameter logs import script options")

    parser.add_argument(
        "--target", type=str, default="all", help="mongo6, mongo8 or all(default)"
    )

    parser.add_argument(
        "--records_num",
        type=int,
        default=DEFAULT_RECORDS_COUNT,
        help="number of records to import.",
    )

    return parser.parse_args()


def get_mongo_operations(records):
    print_colored(
        f'Adapting {get_colored(len(records), "WHITE", restore={"color":"BLUE"})} records into mongo update operations',
        "BLUE",
    )

    ops = {}
    for row in tqdm(records, desc="Adapting records"):
        op = {
            "$push": {
                "user_drugs": {
                    "id": row["id"],
                    "amount": row["amount"],
                    "dose_size": row["dose_size"],
                    "end_date": datetime.combine(
                        datetime.fromisoformat(row["end_date"]), datetime.min.time()
                    ),
                    "priority": row["priority"],
                    "start_date": datetime.combine(
                        datetime.fromisoformat(row["start_date"]), datetime.min.time()
                    ),
                    "drug_id": row["drug_id"],
                    "days": row["days"],
                    "times": row["times"],
                }
            }
        }

        if row["user_id"] not in ops:
            ops[row["user_id"]] = []
        ops[row["user_id"]].append(op)

    print_colored(
        f'Adaption complete. Transformed into {get_colored(len(ops), "WHITE", restore={"color":"GREEN"})} update operations.',
        "GREEN",
    )

    return ops


def import_mongo_user_drugs(operations, conn_params, db, title):
    mongo_client = MongoClient(**conn_params)
    mongo_db = mongo_client[db]
    users_coll = mongo_db["users"]

    print_colored(
        f'[{title}] Executing {get_colored(len(operations), "WHITE", restore={"color":"BLUE"})} operations',
        "BLUE",
    )

    start = time()

    for user_id, ops in tqdm(operations.items(), desc="Executing"):
        updates = [UpdateOne({"_id": user_id}, op) for op in ops]
        for i in range(0, len(updates), 1000):
            users_coll.bulk_write(updates[i : i + 1000])

    end = time()

    return end - start


if __name__ == "__main__":
    args = _parse_args()

    records = import_n_records(DEFAULT_FILE, args.records_num)

    if records == False:
        print_colored(f"[Mongo] Can't continue", "RED")
        exit()

    ops = get_mongo_operations(records)

    print("")

    if args.target == "all" or args.target == "mongo6":
        try:

            time_taken6 = import_mongo_user_drugs(
                ops,
                {
                    "host": MONGO6_HOST,
                    "port": int(MONGO6_PORT),
                    "username": MONGO6_USER,
                    "password": MONGO6_PASSWORD,
                },
                MONGO6_DB,
                "Mongo6",
            )
            print_colored(f"Insert into MongoDB 6 complete.", "GREEN")
        except Exception as ex:
            print_colored(f"Failed to insert in mongo 6: {ex}", "RED")

    time_taken6 = None
    time_taken8 = None

    if args.target == "all" or args.target == "mongo8":
        try:

            time_taken8 = import_mongo_user_drugs(
                ops,
                {
                    "host": MONGO8_HOST,
                    "port": int(MONGO8_PORT),
                    "username": MONGO8_USER,
                    "password": MONGO8_PASSWORD,
                },
                MONGO8_DB,
                "Mongo8",
            )
            print_colored(f"Insert into MongoDB 8 complete.", "GREEN")
        except Exception as ex:
            print_colored(f"Failed to insert in mongo 8: {ex}", "RED")

    if time_taken6 and time_taken8:
        print_colored("Insert complete", "GREEN")

        print_colored(f"Time taken (Mongo6): {time_taken6}s")
        print_colored(f"Time taken (Mongo8): {time_taken8}s")

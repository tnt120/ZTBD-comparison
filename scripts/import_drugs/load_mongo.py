import sys
import os
import json
import pymongo
import argparse
from source.generate_drugs_json import generate_drugs_json


def parse_args():
    parser = argparse.ArgumentParser(description="MongoDB Schema Application Script")

    parser.add_argument(
        "--target", type=str, default="all", help="mongo6, mongo8 or all(default)"
    )

    return parser.parse_args()


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
from common.utils import print_colored

INPUT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "source/drugs.json"
)
TARGET_COLLECTION = "drugs"


def load_into_mongo(host, port, user, password, db_name):
    client = pymongo.MongoClient(host, port=int(port), username=user, password=password)

    db = client[db_name]

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            db[TARGET_COLLECTION].insert_one(doc)

    print_colored("[Mongo] Drugs loaded successfully.", "GREEN")


if __name__ == "__main__":
    args = parse_args()

    if not os.path.exists(INPUT_FILE):
        print_colored(f"Cannot find input drugs.json file. Generating...", "YELLOW")
        generate_drugs_json()

    if args.target == "all" or args.target == "mongo6":
        try:
            print_colored(f"Loading drugs into Mongo 6", "BLUE")
            load_into_mongo(
                MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
            )
        except:
            print_colored("Failed to load drugs into Mongo 6", "RED")

    if args.target == "all" or args.target == "mongo8":
        try:
            print_colored(f"Loading drugs into Mongo 8", "BLUE")
            load_into_mongo(
                MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
            )
        except:
            print_colored("Failed to load drugs into Mongo 8", "RED")

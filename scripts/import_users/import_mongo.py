import sys
import os
import pymongo
import argparse
import json
from datetime import datetime


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
    os.path.dirname(os.path.abspath(__file__)), "source/users.json"
)
TARGET_COLLECTION = "users"


def convert_dates(document):
    date_fields = ["birth_date", "creation_date"]
    for field in date_fields:
        if field in document and isinstance(document[field], str):
            try:
                document[field] = datetime.fromisoformat(
                    document[field].replace("Z", "+00:00")
                )
            except ValueError:
                print(f"Skipping invalid date format: {document[field]}")
    return document


def import_mongo_users(host, port, user, password, db):
    client = pymongo.MongoClient(host, port=int(port), username=user, password=password)

    db = client[db]

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        file_content = f.read()
        data = json.loads(file_content)
        data = [convert_dates(doc) for doc in data]
        db[TARGET_COLLECTION].insert_many(data)
    client.close()


if __name__ == "__main__":
    args = parse_args()

    if args.target == "all" or args.target == "mongo6":
        try:
            import_mongo_users(
                MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
            )
            print_colored(f"Users loaded into MongoDB 6 successfully.", "GREEN")
        except:
            print_colored("Failed to import users in mongo 6", "RED")

    if args.target == "all" or args.target == "mongo8":
        try:
            import_mongo_users(
                MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
            )
            print_colored(f"Users loaded into MongoDB 8 successfully.", "GREEN")
        except Exception as ex:
            print_colored(f"Failed to import users in mongo 8. {ex}", "RED")

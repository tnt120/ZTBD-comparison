import sys
import os
import pymongo
import argparse
import json


def parse_args():
    parser = argparse.ArgumentParser(description="MongoDB Schema Application Script")

    parser.add_argument(
        "--target", type=str, default="all", help="mongo6, mongo8 or all(default)"
    )

    return parser.parse_args()


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
from utils import print_colored

def import_mongo(host, port, user, password, db, input_file, collection):
    client = pymongo.MongoClient(host, port=int(port), username=user, password=password)

    db = client[db]

    with open(input_file, "r", encoding="utf-8") as f:
        file_content = f.read()
        data = json.loads(file_content)
        db[collection].insert_many(data)
    client.close()


if __name__ == "__main__":
    args = parse_args()

    if args.target == "all" or args.target == "mongo6":
        try:
            import_mongo(
                MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB, "source/units.json", "units"
            )
            
            print_colored(f"Units loaded into MongoDB 6 successfully.", "GREEN")
            import_mongo(
                MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB, "source/parameters.json", "parameters"
            )
            print_colored(f"Units loaded into MongoDB 6 successfully.", "GREEN")
        except Exception as ex:
            print_colored(f"Failed to import parameters or logs in mongo 6. {ex}", "RED")

    if args.target == "all" or args.target == "mongo8":
        try:
            import_mongo(
                MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB, "source/units.json", "units"
            )
            
            print_colored(f"Units loaded into MongoDB 8 successfully.", "GREEN")
            import_mongo(
                MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB, "source/parameters.json", "parameters"
            )
            print_colored(f"Units loaded into MongoDB 8 successfully.", "GREEN")
        except Exception as ex:
            print_colored(f"Failed to import parameters or logs in mongo 8. {ex}", "RED")

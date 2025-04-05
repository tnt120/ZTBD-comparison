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
from common.utils import print_colored


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

    units_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "source/units.json"
    )
    parameters_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "source/parameters.json"
    )

    if args.target == "all" or args.target == "mongo6":
        try:
            import_mongo(
                MONGO6_HOST,
                MONGO6_PORT,
                MONGO6_USER,
                MONGO6_PASSWORD,
                MONGO6_DB,
                units_file_path,
                "units",
            )

            print_colored(f"Units loaded into MongoDB 6 successfully.", "GREEN")
            import_mongo(
                MONGO6_HOST,
                MONGO6_PORT,
                MONGO6_USER,
                MONGO6_PASSWORD,
                MONGO6_DB,
                parameters_file_path,
                "parameters",
            )
            print_colored(f"Units loaded into MongoDB 6 successfully.", "GREEN")
        except Exception as ex:
            print_colored(
                f"Failed to import parameters or logs in mongo 6. {ex}", "RED"
            )

    if args.target == "all" or args.target == "mongo8":
        try:
            import_mongo(
                MONGO8_HOST,
                MONGO8_PORT,
                MONGO8_USER,
                MONGO8_PASSWORD,
                MONGO8_DB,
                units_file_path,
                "units",
            )

            print_colored(f"Units loaded into MongoDB 8 successfully.", "GREEN")
            import_mongo(
                MONGO8_HOST,
                MONGO8_PORT,
                MONGO8_USER,
                MONGO8_PASSWORD,
                MONGO8_DB,
                parameters_file_path,
                "parameters",
            )
            print_colored(f"Units loaded into MongoDB 8 successfully.", "GREEN")
        except Exception as ex:
            print_colored(
                f"Failed to import parameters or logs in mongo 8. {ex}", "RED"
            )

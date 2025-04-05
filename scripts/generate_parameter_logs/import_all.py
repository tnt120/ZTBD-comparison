import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
from generate_parameter_logs.defaults import DEFAULT_RECORDS_COUNT, DEFAULT_FILE
from common.utils import print_colored, get_colored, import_n_records
from generate_parameter_logs.import_postgres import import_postgres_parameters
from generate_parameter_logs.import_mysql import import_mysql_parameters
from generate_parameter_logs.import_mongo import (
    import_mongo_parameters,
    get_mongo_operations,
)


def _parse_args():
    parser = argparse.ArgumentParser(description="Parameter logs import script options")

    parser.add_argument(
        "--records_num",
        type=int,
        default=DEFAULT_RECORDS_COUNT,
        help="number of records to import.",
    )

    return parser.parse_args()


def import_all(records_num):
    print_colored(
        f'Collecting {get_colored(records_num, "WHITE", restore={"color": "BLUE"})} records',
        "BLUE",
    )

    records = import_n_records(DEFAULT_FILE, records_num)

    if records == False:
        print_colored("Can't continue", "RED")
        exit()

    print("")

    time_taken_pg = 0
    time_taken_mysql = 0
    time_taken6 = 0
    time_taken8 = 0

    try:
        time_taken_pg = import_postgres_parameters(len(records), records)
        print_colored(f"Postgres insert complete.", "GREEN")
    except Exception as ex:
        print_colored(f"Failed to insert in postgres: {ex}", "RED")

    print("")

    try:
        time_taken_mysql = import_mysql_parameters(len(records), records)
        print_colored(f"MySQL insert complete.", "GREEN")
    except Exception as ex:
        print_colored(f"Failed to insert in mysql: {ex}", "RED")

    print("")

    ops = get_mongo_operations(records)

    print("")

    try:
        time_taken6 = import_mongo_parameters(
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
        print_colored(f"Mongo6 insert complete.", "GREEN")
    except Exception as ex:
        print_colored(f"Failed to insert in mongo6: {ex}", "RED")

    try:
        time_taken8 = import_mongo_parameters(
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
        print_colored(f"Mongo8 insert complete.", "GREEN")
    except Exception as ex:
        print_colored(f"Failed to insert in mongo8: {ex}", "RED")

    print_colored(f"\nInserts complete", "GREEN")
    print_colored(f'Postgres: {get_colored(time_taken_pg, "WHITE")}s', "BLUE")
    print_colored(f'MySQL: {get_colored(time_taken_mysql, "WHITE")}s', "BLUE")
    print_colored(f'Mongo 6: {get_colored(time_taken6,"WHITE")}s', "BLUE")
    print_colored(f'Mongo 8: {get_colored(time_taken8, "WHITE")}s', "BLUE")


if __name__ == "__main__":
    args = _parse_args()

    import_all(args.records_num)

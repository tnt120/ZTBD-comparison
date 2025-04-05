import os
import sys
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
from common.utils import print_colored
from common.truncate_single import (
    truncate_in_postgres,
    truncate_in_mysql,
    truncate_in_mongo,
)


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Parameter logs truncate script options"
    )

    parser.add_argument(
        "--targets",
        type=str,
        default="all",
        help="what to truncate; comma separated list of: pg; mysql; mongo6; mongo8; or all (default)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    targets = ["pg", "mysql", "mongo6", "mongo8"]

    if args.targets != "all":
        new_targets = {
            x.strip().lower()
            for x in args.targets.split(",")
            if x.strip() and x.strip().lower() in targets
        }

        if len(new_targets) != 0:
            targets = new_targets

    for target in targets:
        print("")

        match target:
            case "pg":
                print_colored("Truncating postgres...", "BLUE")

                truncate_in_postgres("drugs_logs")
            case "mysql":
                print_colored("Truncating mysql...", "BLUE")

                truncate_in_mysql("drugs_logs")
            case "mongo6":
                print_colored("Truncating mongo 6...", "BLUE")

                truncate_in_mongo(
                    MONGO6_HOST,
                    MONGO6_PORT,
                    MONGO6_USER,
                    MONGO6_PASSWORD,
                    MONGO6_DB,
                    "users",
                    "user_drugs",
                )
            case "mongo8":
                print_colored("Truncating mongo 8...", "BLUE")

                truncate_in_mongo(
                    MONGO8_HOST,
                    MONGO8_PORT,
                    MONGO8_USER,
                    MONGO8_PASSWORD,
                    MONGO8_DB,
                    "users",
                    "parameters_logs",
                )

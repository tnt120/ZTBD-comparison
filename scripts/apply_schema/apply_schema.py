import sys
import os
from apply_postgres import apply_postgres_schema
from apply_mysql import apply_mysql_schema
from apply_mongo import apply_mongo_schema

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
from common.utils import print_colored


def apply_schema():
    print_colored("1. Applying Postgres schema:", "BLUE")
    apply_postgres_schema()

    print_colored("\n2. Applying Mysql schema: ", "BLUE")
    apply_mysql_schema()

    print_colored("\n3. Applying Mongo 6 schema: ", "BLUE")
    apply_mongo_schema(
        MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
    )
    print_colored(f"MongoDB 6 schema applied successfully.", "GREEN")

    print_colored("\n4. Applying Mongo 8 schema: ", "BLUE")
    apply_mongo_schema(
        MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
    )
    print_colored(f"MongoDB 8 schema applied successfully.", "GREEN")


if __name__ == "__main__":
    apply_schema()

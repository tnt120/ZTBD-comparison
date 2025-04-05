import sys
import os
from drop_postgres import drop_postgres_schema
from drop_mysql import drop_mysql_schema
from drop_mongo import drop_mongo_schema

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
from common.utils import print_colored


def drop_schema():
    print_colored("1. Dropping Postgres schema:", "BLUE")
    drop_postgres_schema()

    print_colored("\n2. Dropping Mysql schema: ", "BLUE")
    drop_mysql_schema()

    print_colored("\n3. Dropping Mongo 6 schema: ", "BLUE")
    drop_mongo_schema(MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB)
    print_colored(f"MongoDB 6 schema dropped successfully.", "GREEN")

    print_colored("\n4. Dropping Mongo 8 schema: ", "BLUE")
    drop_mongo_schema(MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB)
    print_colored(f"MongoDB 8 schema dropped successfully.", "GREEN")


if __name__ == "__main__":
    drop_schema()

import sys
import os
from truncate_postgres import truncate_postgres_schema
from truncate_mysql import truncate_mysql_schema
from truncate_mongo import truncate_mongo_schema

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
from utils import print_colored


if __name__ == "__main__":
	print_colored("1. Truncating Postgres schema:", "BLUE")
	truncate_postgres_schema()

	print_colored("\n2. Truncating Mysql schema: ", "BLUE")
	truncate_mysql_schema()

	print_colored("\n3. Truncating Mongo 6 schema: ", "BLUE")
	truncate_mongo_schema(MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB)
	print_colored(f"MongoDB 6 schema truncated successfully.", "GREEN")

	print_colored("\n4. Truncating Mongo 8 schema: ", "BLUE")
	truncate_mongo_schema(MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB)
	print_colored(f"MongoDB 8 schema truncated successfully.", "GREEN")
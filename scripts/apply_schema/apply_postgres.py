import sys
import os
import psycopg2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from env import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
from utils import print_colored

FILE_PATH='source/postgre.sql'

def apply_postgres_schema():
	conn = psycopg2.connect(
		host=POSTGRES_HOST,
		user=POSTGRES_USER,
		password=POSTGRES_PASSWORD,
		dbname=POSTGRES_DB,
		port=POSTGRES_PORT
	)

	conn.autocommit = True

	cursor = conn.cursor()

	with open(FILE_PATH, 'r') as file:
		sql_commands = file.read()

	sql_statements = sql_commands.split(';')

	for statement in sql_statements:
		if statement.strip():
			try:
				cursor.execute(statement.strip())
			except psycopg2.Error as e:
				print_colored(f"Error executing statement: {e}","RED")
				continue 

	print_colored(f"Postgre sql schema applied successfully", "GREEN")


if __name__ == "__main__":
	apply_postgres_schema()
import sys
import os
import psycopg2
from psycopg2 import sql

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from env import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
from utils import print_colored

def truncate_postgres_schema():
	conn = psycopg2.connect(
		host=POSTGRES_HOST,
		user=POSTGRES_USER,
		password=POSTGRES_PASSWORD,
		dbname=POSTGRES_DB,
		port=POSTGRES_PORT
	)

	cursor = conn.cursor()

	cursor.execute("""
		SELECT table_name 
		FROM information_schema.tables
		WHERE table_schema = 'public'
	""")
	
	tables = cursor.fetchall()

	for table in tables:
		table_name = table[0]
		cursor.execute(sql.SQL("TRUNCATE TABLE {} CASCADE").format(sql.Identifier(table_name)))

	conn.commit()

	print_colored(f"Postgre sql schema truncated successfully", "GREEN")


if __name__ == "__main__":
	truncate_postgres_schema()
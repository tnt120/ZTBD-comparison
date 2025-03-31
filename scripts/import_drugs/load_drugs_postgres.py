import sys
import os
import psycopg2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from env import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
from utils import print_colored

def load_postgres_drugs():
	conn = psycopg2.connect(
		dbname=POSTGRES_DB,
		user=POSTGRES_USER,
		password=POSTGRES_PASSWORD,
		host=POSTGRES_HOST,
		port=POSTGRES_PORT
	)
	cursor = conn.cursor()

	with open("source\drugs.sql", "r", encoding="utf-8") as file:
		sql = file.read()

	cursor.execute(sql)

	print_colored("[Postgres] Drugs loaded successfully.", "GREEN")

	conn.commit()
	cursor.close()
	conn.close()

if __name__ == "__main__":
	load_postgres_drugs()
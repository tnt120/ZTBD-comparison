import sys
import os
import psycopg2
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from env import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
from utils import print_colored


def load_postgres_drug_packs():
	conn = psycopg2.connect(
		dbname=POSTGRES_DB,
		user=POSTGRES_USER,
		password=POSTGRES_PASSWORD,
		host=POSTGRES_HOST,
		port=POSTGRES_PORT
	)
	cursor = conn.cursor()

	with open("source/drug_packs.sql", "r", encoding="utf-8") as file:
		sql = file.read()

	pattern = re.compile(r"INSERT INTO public\.drug_packs \(\s*id,\s*(.*?)\) VALUES \((\d+),\s*(.*?)\);", re.DOTALL)

	def remove_id_column(match):
		columns = match.group(1)
		values = match.group(3)
		return f"INSERT INTO public.drug_packs ({columns}) VALUES ({values});"

	modified_sql = pattern.sub(remove_id_column, sql)

	cursor.execute(modified_sql)

	conn.commit()

	print_colored(f"[Postgres] Drug packs loaded successfully.", "GREEN")

	cursor.close()
	conn.close()


if __name__ == "__main__":
	load_postgres_drug_packs()
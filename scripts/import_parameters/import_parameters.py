import sys
import os
from import_postgres import load_postgres
from import_mysql import load_mysql
from import_mongo import import_mongo


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
from utils import print_colored


if __name__ == "__main__":
	print_colored("Postgres", "BLUE")
	try:
		load_postgres("source/units.sql", "Units")
		load_postgres("source/parameters.sql", "Parameters")
	except:
		print_colored("Failed loading postgres", "RED")

	print_colored("MySQL", "BLUE")
	try:
		load_mysql("source/units.sql", "Units")
		load_mysql("source/parameters.sql", "Parameters")
	except:
		print_colored("Failed loading mysql", "RED")

	print_colored("Mongo 6", "BLUE")
	try:
		import_mongo(
			MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB, "source/units.json", "units"
		)
		
		print_colored(f"[Mongo 6] Units loaded successfully.", "GREEN")
		
		import_mongo(
			MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB, "source/parameters.json", "parameters"
		)

		print_colored(f"[Mongo 6] Units loaded successfully.", "GREEN")
	except:
		print_colored("Failed loading mongo 6", "RED")

	print_colored("Mongo 8", "BLUE")
	try:
		import_mongo(
			MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB, "source/units.json", "units"
		)
		
		print_colored(f"[Mongo 8] Units loaded successfully.", "GREEN")
		
		import_mongo(
			MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB, "source/parameters.json", "parameters"
		)

		print_colored(f"[Mongo 8] Units loaded successfully.", "GREEN")
	except:
		print_colored("Failed loading mongo 8", "RED")

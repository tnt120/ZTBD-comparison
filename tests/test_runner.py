import argparse
import importlib.util
import os
import sys
from time import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from scripts.common.utils import handle_test_params, print_colored, get_colored
from scripts.common.handle_connection import make_connection, disconnect

def load_test_module(folder):
	path = os.path.join(folder, "test.py")
	if not os.path.isfile(path):
		raise FileNotFoundError(f"Plik {path} nie istnieje.")


	spec = importlib.util.spec_from_file_location("test_module", path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module

def parse_args():
	parser = argparse.ArgumentParser(description="MongoDB Schema Application Script")

	parser.add_argument(
		"--tests", type=str, default="all", help="mongo6, mongo8 or all(default)"
	)

	parser.add_argument(
		"--db", type=str, default="all", help="mongo6, mongo8 or all(default)"
	)

	return parser.parse_args()


if __name__ == "__main__":

	args = parse_args()

	test_names = [name for name in os.listdir('.') if os.path.isdir(name)]

	test_names = handle_test_params(args.tests, test_names)

	dbs = handle_test_params(args.db, ["pg", "mysql", "mongo6", "mongo8"])

	connections = [make_connection(db) for db in dbs]

	print_colored(f'Running tests on {get_colored(", ".join(dbs), "WHITE", restore={"color":"YELLOW"})} databases.', "YELLOW")

	for test in test_names:
		try: 
			test_module = load_test_module(test)
		except FileNotFoundError as e:
			print_colored(f"Couldn't load test named {get_colored(test, "WHITE", restore={"color": "RED"})}. Err: {e}", "RED")
			continue

		print_colored(f'\nRunning test: {get_colored(test,"WHITE")}\n', "BLUE")
		
		for conn, db in connections:
			print_colored(f"{db}: ", "BLUE", newline=False)

			if hasattr(test_module, "execute"):

				try:
					start_time = time()
					test_module.execute(db, conn)
					end_time = time()

					time_taken = end_time - start_time
					print(f"{time_taken}{get_colored("s", "BLUE")}")
				except Exception as e:
					print_colored(f"\nError executing test for {get_colored(test, "WHITE", restore={"color": "RED"})}.{get_colored(db, "WHITE", restore={"color": "RED"})}. Error: {e}", "RED")

			if hasattr(test_module, "after"):
				try:
					test_module.after(db, conn)
				except Exception as e:
					print_colored(f'Error running cleanup for {get_colored(test, "WHITE", restore={"color": "RED"})}.{get_colored(db, "WHITE", restore={"color": "RED"})}. Error: {e}', "RED")


	for connection, db in connections:
		disconnect(connection, db)

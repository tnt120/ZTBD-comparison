import sys
import os
from load_drug_packs_mysql import load_mysql_drug_packs
from load_drugs_mysql import load_mysql_drugs

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import print_colored


if __name__ == "__main__":
	print_colored("1. Loading drugs into MySQL: ", "BLUE")
	load_mysql_drugs()

	print_colored("\n2. Loading drug packs into MySQL: ", "BLUE")
	load_mysql_drug_packs()
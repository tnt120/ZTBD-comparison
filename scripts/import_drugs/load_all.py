import sys
import os
from load_drug_packs_postgres import load_postgres_drug_packs
from load_drugs_postgres import load_postgres_drugs
from load_drug_packs_mysql import load_mysql_drug_packs
from load_drugs_mysql import load_mysql_drugs
from load_mongo import load_into_mongo, INPUT_FILE
from source.generate_drugs_json import generate_drugs_json


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
from common.utils import print_colored


def load_drugs():
    print_colored("1. Loading drugs", "BLUE")
    try:
        load_postgres_drugs()
    except:
        print_colored("Failed loading postgres")
    load_mysql_drugs()

    if not os.path.exists(INPUT_FILE):
        print_colored(
            f"Cannot find input drugs.json for mongodb file. Generating...", "YELLOW"
        )
        generate_drugs_json()

    print_colored("Mongo 6 >", "BLUE", None, "BRIGHT")
    load_into_mongo(MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB)
    print_colored("Mongo 8 >", "BLUE", None, "BRIGHT")
    load_into_mongo(MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB)

    print_colored("\n2. Loading drug packs: ", "BLUE")
    load_postgres_drug_packs()
    load_mysql_drug_packs()


if __name__ == "__main__":
    load_drugs()

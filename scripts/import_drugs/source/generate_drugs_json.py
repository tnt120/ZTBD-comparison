import re
import json
import csv
from collections import defaultdict
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from common.utils import print_colored

DRUGS_INPUT_FILE = "drugs.sql"
DRUG_PACKS_INPUT_FILE = "drug_packs.sql"


def parse_insert_sql(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        matches = re.findall(
            r"INSERT INTO (?:\w+\.)?`?(\w+)`? \((.*?)\) VALUES\s*\((.*?)\);",
            content,
            re.DOTALL | re.IGNORECASE,
        )
        if not matches:
            raise ValueError(
                f"[{file_path}] Insert statements not found. Make sure file exists and is valid."
            )

        result = []

        for table, columns_str, values_str in matches:
            columns = [col.strip().strip("`") for col in columns_str.split(",")]

            reader = csv.reader([values_str], skipinitialspace=True, quotechar="'")
            values = next(reader)

            clean = lambda x: None if x.upper() == "NULL" else x.strip()
            values = list(map(clean, values))

            row_dict = dict(zip(columns, values))
            result.append(row_dict)

        return result
    except Exception as ex:
        print_colored(f"Failed to read data from {file_path}. Exception: {ex}", "RED")


def generate_drugs_json():
    drugs = parse_insert_sql(DRUGS_INPUT_FILE)
    drug_packs = parse_insert_sql(DRUG_PACKS_INPUT_FILE)

    print_colored(f"Found {len(drugs)} drugs and {len(drug_packs)} drug packs.", "BLUE")

    packs_by_drug = defaultdict(list)
    for pack in drug_packs:
        try:
            drug_id = int(pack["drug_id"])
        except ValueError:
            continue
        del pack["drug_id"]
        packs_by_drug[drug_id].append(pack)

    mongo_docs = []
    for drug in drugs:
        drug_id = int(drug["id"])
        drug["_id"] = drug_id
        del drug["id"]
        drug["drug_packs"] = packs_by_drug.get(drug_id, [])
        mongo_docs.append(drug)

    with open("drugs.json", "w", encoding="utf-8") as f:
        for doc in mongo_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print_colored("File drugs.json generated successfully.", "GREEN")


if __name__ == "__main__":
    generate_drugs_json()

import re
import json
from collections import defaultdict

def parse_insert_sql(file_path):
    import csv
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("\n==== Podgląd początku pliku ====")
    print(content[:500])
    print("=================================\n")

    matches = re.findall(
        r"INSERT INTO (?:\w+\.)?`?(\w+)`? \((.*?)\) VALUES\s*\((.*?)\);",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if not matches:
        raise ValueError("❌ Nie znaleziono żadnych INSERT INTO ... VALUES (...);")

    print(f"Znaleziono {len(matches)} rekordów do sparsowania")

    result = []

    for table, columns_str, values_str in matches:
        columns = [col.strip().strip('`') for col in columns_str.split(',')]

        reader = csv.reader([values_str], skipinitialspace=True, quotechar="'")
        values = next(reader)

        clean = lambda x: None if x.upper() == "NULL" else x.strip()
        values = list(map(clean, values))

        row_dict = dict(zip(columns, values))
        result.append(row_dict)

    return result


drugs = parse_insert_sql("drugs.sql")
drug_packs = parse_insert_sql("drug_packs.sql")

packs_by_drug = defaultdict(list)
for pack in drug_packs:
    print("Przykład drug_packs:", pack)
    if 'drug_id' not in pack:
        print("⚠️ Brakuje pola 'drug_id' w:", pack)
        continue
    try:
        drug_id = int(pack['drug_id'])
    except ValueError:
        print("⚠️ Błędna wartość drug_id:", pack['drug_id'], "→", pack)
        continue
    del pack['drug_id']
    packs_by_drug[drug_id].append(pack)

mongo_docs = []
for drug in drugs:
    drug_id = int(drug['id'])
    drug['_id'] = drug_id
    del drug['id']
    drug['drug_packs'] = packs_by_drug.get(drug_id, [])
    mongo_docs.append(drug)

with open("mongo_drugs.json", "w", encoding="utf-8") as f:
    for doc in mongo_docs:
        f.write(json.dumps(doc, ensure_ascii=False) + '\n')

print("Zrobione! Plik mongo_drugs.json gotowy do importu.")

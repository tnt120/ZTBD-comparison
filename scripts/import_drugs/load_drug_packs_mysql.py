import mysql.connector
import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from env import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from utils import print_colored


def load_mysql_drug_packs():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
    )
    cursor = conn.cursor()

    with open("source/drug_packs.sql", "r", encoding="utf-8") as file:

        pattern = re.compile(
            r"INSERT INTO public\.drug_packs \(\s*id,\s*(.*?)\) VALUES \((\d+),\s*(.*?)\);",
            re.DOTALL,
        )

        def remove_id_column(match):
            columns = match.group(1)
            values = match.group(3)
            return f"INSERT INTO public.drug_packs ({columns}) VALUES ({values});"

        modified_sql = pattern.sub(remove_id_column, file.read())

        for line in modified_sql.split(";"):
            line = line.strip()
            if not line or not line.lower().startswith("insert"):
                continue

            line = re.sub(
                r"INSERT INTO\s+public\.", "INSERT INTO ", line, flags=re.IGNORECASE
            )
            cursor.execute(line)

    conn.commit()

    print_colored(f"[MySQL] Drug packs loaded successfully.", "GREEN")

    cursor.close()


if __name__ == "__main__":
    load_mysql_drug_packs()

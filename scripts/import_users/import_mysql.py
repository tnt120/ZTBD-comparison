import mysql.connector
import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from env import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from utils import print_colored


def load_mysql_users():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
    )
    cursor = conn.cursor()

    with open("source/users.sql", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or not line.lower().startswith("insert"):
                continue

            line = re.sub(
                r"INSERT INTO\s+public\.", "INSERT INTO ", line, flags=re.IGNORECASE
            )
            cursor.execute(line)

    conn.commit()

    print_colored("[MySQL] Users loaded successfully.", "GREEN")

    cursor.close()


if __name__ == "__main__":
    load_mysql_users()

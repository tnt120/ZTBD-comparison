import sys
import os
import psycopg2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from env import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
)
from common.utils import print_colored


def load_postgres_users():
    conn = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )
    cursor = conn.cursor()

    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "source/users.sql"
    )

    with open(file_path, "r", encoding="utf-8") as file:
        sql = file.read()

    cursor.execute(sql)

    print_colored("[Postgres] Users loaded successfully.", "GREEN")

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    load_postgres_users()

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


def load_postgres(input_file, table_name):
    conn = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )
    cursor = conn.cursor()

    with open(input_file, "r", encoding="utf-8") as file:
        sql = file.read()

    cursor.execute(sql)

    print_colored(f"[Postgres] {table_name} loaded successfully.", "GREEN")

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    units_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "source/units.sql"
    )
    parameters_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "source/parameters.sql"
    )

    load_postgres(units_file_path, "Units")
    load_postgres(parameters_file_path, "Parameters")

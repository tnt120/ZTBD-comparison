import sys
import os
import mysql.connector

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from common.utils import print_colored


def drop_mysql_schema():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
    )
    cursor = conn.cursor()

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

    conn.commit()

    print_colored(f"MySQL schema dropped successfully", "GREEN")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    drop_mysql_schema()

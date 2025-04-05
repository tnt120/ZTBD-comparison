import sys
import os
import mysql.connector

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from common.utils import print_colored

FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source/mysql.sql")


def apply_mysql_schema():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
    )
    cursor = conn.cursor()

    with open(FILE_PATH, "r") as file:
        sql_commands = file.read()

    for command in sql_commands.split(";"):
        if command.strip():
            try:
                cursor.execute(command.strip())
            except mysql.connector.Error as err:
                print_colored(f"Error executing command: {err}", "RED")
                continue
    conn.commit()

    print_colored(f"MySQL schema applied successfully", "GREEN")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    apply_mysql_schema()

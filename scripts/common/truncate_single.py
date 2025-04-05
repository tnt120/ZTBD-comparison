import psycopg2
from psycopg2 import sql
import mysql.connector
import pymongo
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from env import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
)
from env import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from common.utils import print_colored


def truncate_in_postgres(table_name):
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        port=POSTGRES_PORT,
    )

    cursor = conn.cursor()

    cursor.execute(sql.SQL(f"TRUNCATE TABLE {table_name} CASCADE"))

    conn.commit()

    print_colored(f"Postgres '{table_name}' truncated successfully", "GREEN")


def truncate_in_mysql(table_name):
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        port=MYSQL_PORT,
    )
    cursor = conn.cursor()

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    cursor.execute(f"TRUNCATE TABLE {table_name}")

    conn.commit()

    print_colored(f"MySQL '{table_name}' truncated successfully", "GREEN")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    cursor.close()
    conn.close()


def truncate_in_mongo(host, port, user, password, db, collection, list=None):
    client = pymongo.MongoClient(host, port=int(port), username=user, password=password)

    db = client[db]
    target = db[collection]

    if list == None:
        target.delete_many({})

        print_colored(f"Mongo '{collection}' truncated successfully", "GREEN")
    else:
        target.update_many({}, {"$set": {list: []}})

        print_colored(f"Mongo '{collection}.{list}' truncated successfully", "GREEN")

    client.close()

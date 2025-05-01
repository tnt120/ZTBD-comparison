import uuid
from faker import Faker
from scripts.test_utils.insert_revert import (
    revert_insert_postgres,
    revert_insert_mysql,
    revert_insert_mongo,
)

fake = Faker()
unit_id = str(uuid.uuid4())


def execute(db, conn):
    name = fake.word()
    symbol = fake.word()

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        query = """
			INSERT INTO units (id, name, symbol)
			VALUES (%s, %s, %s);
		"""
        cursor.execute(
            query,
            (
                unit_id,
                name,
                symbol,
            ),
        )

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["units"]

        document = {
            "_id": unit_id,
            "name": name,
            "symbol": symbol,
        }

        _ = collection.insert_one(document)


def after(db, conn):
    if db == "pg":
        revert_insert_postgres(conn, "units", [unit_id])
    elif db == "mysql":
        revert_insert_mysql(conn, "units", [unit_id])
    elif db in ["mongo6", "mongo8"]:
        revert_insert_mongo(conn, "units", [unit_id])

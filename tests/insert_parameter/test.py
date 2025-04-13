import uuid
from scripts.test_utils.insert_revert import (
    revert_insert_postgres,
    revert_insert_mysql,
    revert_insert_mongo,
)


param_id = str(uuid.uuid4())


def execute(db, conn):
    unit_id = "873c12ae-9b08-46ab-8957-8363552895dd"
    hint = "Podana w kg"
    max_standard_value = 5
    min_standard_value = 0.5
    max_value = 7.5
    min_value = 0
    name = "Ciśnienie krwi"

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        query = """
			INSERT INTO parameters (id, hint, max_standard_value, max_value, min_standard_value, min_value, name, unit_id)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
		"""
        cursor.execute(
            query,
            (
                param_id,
                hint,
                max_standard_value,
                max_value,
                min_standard_value,
                min_value,
                name,
                unit_id,
            ),
        )

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["parameters"]

        document = {
            "_id": param_id,
            "hint": hint,
            "max_standard_value": max_standard_value,
            "max_value": max_value,
            "min_standard_value": min_standard_value,
            "min_value": min_value,
            "name": name,
            "unit_id": unit_id,
        }

        _ = collection.insert_one(document)


def after(db, conn):
    if db == "pg":
        revert_insert_postgres(conn, "parameters", [param_id])
    elif db == "mysql":
        revert_insert_mysql(conn, "parameters", [param_id])
    elif db in ["mongo6", "mongo8"]:
        revert_insert_mongo(conn, "parameters", [param_id])

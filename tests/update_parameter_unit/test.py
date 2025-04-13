from scripts.test_utils.update_revert import (
    revert_update_postgres,
    revert_update_mysql,
    revert_update_mongo,
)

param_id = "e2eaf170-dd31-41eb-816f-9b3c229a8773"
new_unit_id = "1e7dd989-cde2-474c-9ce2-f5712d99624f"
prev_parameter = None


def before(db, conn):
    global prev_parameter

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parameters WHERE id = %s", (param_id,))
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        prev_parameter = dict(zip(columns, row))
    elif db in ["mongo6", "mongo8"]:
        collection = conn["parameters"]
        param = collection.find_one({"_id": param_id})
        prev_parameter = param


def execute(db, conn):

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE parameters SET unit_id = %s WHERE id = %s", (new_unit_id, param_id)
        )
        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        collection.update_one({"_id": param_id}, {"$set": {"unit_id": new_unit_id}})


def after(db, conn):
    if db == "pg":
        revert_update_postgres(conn, "parameters", [prev_parameter], "id")
    elif db == "mysql":
        revert_update_mysql(conn, "parameters", [prev_parameter], "id")
    elif db in ["mongo6", "mongo8"]:
        revert_update_mongo(conn, "parameters", [prev_parameter])

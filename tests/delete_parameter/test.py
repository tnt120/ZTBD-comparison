from scripts.test_utils.delete_revert import (
    revert_deletion_postgres,
    revert_deletion_mysql,
    revert_deletion_mongo,
)


param_id = "a2ed45cc-0538-45c3-a965-f7e21cfc867a"
prev_parameter = None


def before(db, conn):
    global prev_parameter

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parameters_logs WHERE id = %s", (param_id,))
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        prev_parameter = dict(zip(columns, row))
    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        param = collection.find_one({"parameters_logs.id": param_id})
        prev_parameter = param


def execute(db, conn):
    return
    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        query = """
			DELETE FROM parameters_logs WHERE id = %s
		"""
        cursor.execute(query, (param_id,))

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        collection.delete_one({"parameters_logs.id": param_id})


def after(db, conn):
    if db == "pg":
        revert_deletion_postgres(conn, "parameters_logs", [prev_parameter])
    elif db == "mysql":
        revert_deletion_mysql(conn, "parameters_logs", [prev_parameter])
    elif db in ["mongo6", "mongo8"]:
        revert_deletion_mongo(
            conn,
            "users",
            [prev_parameter],
            "parameters_logs",
            prev_parameter["user_id"],
        )

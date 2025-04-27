from scripts.test_utils.delete_revert import (
    revert_deletion_postgres,
    revert_deletion_mysql,
    revert_deletion_mongo,
)


param_id = "d2b5904e-054f-4aa1-b823-09fd60f5a814"
prev_parameter = None
user_id = None


def before(db, conn):
    global prev_parameter, user_id

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parameters_logs WHERE id = %s", (param_id,))
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        prev_parameter = dict(zip(columns, row))
    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        user = collection.find_one({"parameters_logs._id": param_id})
        if user:
            prev_parameter = next(
                (
                    log
                    for log in user.get("parameters_logs", [])
                    if log["_id"] == param_id
                ),
                None,
            )
            user_id = user["_id"]
        else:
            prev_parameter = None


def execute(db, conn):
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
            user_id,
        )

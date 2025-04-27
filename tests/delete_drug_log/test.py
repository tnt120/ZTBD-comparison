from scripts.test_utils.delete_revert import (
    revert_deletion_postgres,
    revert_deletion_mysql,
    revert_deletion_mongo,
)


param_id = "444848e3-5a57-4809-a639-33774e0c767b"
prev_parameter = None
user_id = None


def before(db, conn):
    global prev_parameter, user_id

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drugs_logs WHERE id = %s", (param_id,))
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        prev_parameter = dict(zip(columns, row))
    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        user = collection.find_one({"drugs_logs._id": param_id})
        if user:
            prev_parameter = next(
                (log for log in user.get("drugs_logs", []) if log["_id"] == param_id),
                None,
            )
            user_id = user["_id"]
        else:
            prev_parameter = None


def execute(db, conn):
    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        query = """
			DELETE FROM drugs_logs WHERE id = %s
		"""
        cursor.execute(query, (param_id,))

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        collection.delete_one({"drugs_logs.id": param_id})


def after(db, conn):
    if db == "pg":
        revert_deletion_postgres(conn, "drugs_logs", [prev_parameter])
    elif db == "mysql":
        revert_deletion_mysql(conn, "drugs_logs", [prev_parameter])
    elif db in ["mongo6", "mongo8"]:
        revert_deletion_mongo(
            conn,
            "users",
            [prev_parameter],
            "drugs_logs",
            user_id,
        )

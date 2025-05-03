from scripts.test_utils.delete_revert import (
    revert_deletion_postgres,
    revert_deletion_mysql,
    revert_deletion_mongo,
)

parameter_id = "d9b8dae2-51e4-4950-bbff-ccc9560d20e2"
prev_parameter = None
prev_parameters_logs = []
affected_user_id = None


def before(db, conn):
    global prev_parameter, prev_parameters_logs, affected_user_id

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()

        def fetch_all(query, params=None):
            cursor.execute(query, params)
            cols = [desc[0] for desc in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM parameters WHERE id = %s", (parameter_id,))
        row = cursor.fetchone()
        if row:
            cols = [desc[0] for desc in cursor.description]
            prev_parameter = dict(zip(cols, row))

        prev_parameters_logs = fetch_all("SELECT * FROM parameters_logs WHERE parameter_id = %s", (parameter_id,))
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        prev_parameter = conn["parameters"].find_one({"_id": parameter_id})
        prev_parameters_logs = []
        user = conn["users"].find_one({"parameters_logs.parameter_id": parameter_id})
        if user:
            for log in user.get("parameters_logs", []):
                if log.get("parameter_id") == parameter_id:
                    prev_parameters_logs.append(log)
            affected_user_id = user["_id"]


def execute(db, conn):
    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM parameters_logs WHERE parameter_id = %s", (parameter_id,))
        cursor.execute("DELETE FROM parameters WHERE id = %s", (parameter_id,))
        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        conn["parameters"].delete_one({"_id": parameter_id})
        if affected_user_id:
            conn["users"].update_one(
                {"_id": affected_user_id},
                {"$pull": {"parameters_logs": {"parameter_id": parameter_id}}}
            )


def after(db, conn):
    if prev_parameter is None:
        print("No parameter to restore.")
        return

    if db == "pg":
        revert_deletion_postgres(conn, "parameters", [prev_parameter])
        if prev_parameters_logs:
            revert_deletion_postgres(conn, "parameters_logs", prev_parameters_logs)

    elif db == "mysql":
        revert_deletion_mysql(conn, "parameters", [prev_parameter])
        if prev_parameters_logs:
            revert_deletion_mysql(conn, "parameters_logs", prev_parameters_logs)

    elif db in ["mongo6", "mongo8"]:
        conn["parameters"].insert_one(prev_parameter)
        if prev_parameters_logs and affected_user_id:
            for log in prev_parameters_logs:
                conn["users"].update_one(
                    {"_id": affected_user_id},
                    {"$push": {"parameters_logs": log}},
                    upsert=True
                )

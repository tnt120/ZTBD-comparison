from scripts.test_utils.update_revert import (
    revert_update_postgres,
    revert_update_mysql,
    revert_update_mongo,
)

param_id = "39828a6f-33ca-4740-a632-e9fd9c44fa9d"
prev_param_logs = []


def before(db, conn):
    global prev_param_logs

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM parameters_logs WHERE parameter_id = %s", (param_id,)
        )
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        prev_param_logs = [dict(zip(columns, row)) for row in rows]
    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        prev_param_logs = list(
            collection.aggregate(
                [
                    {"$unwind": "$parameters_logs"},
                    {"$match": {"parameters_logs.parameter_id": param_id}},
                    {"$replaceRoot": {"newRoot": "$parameters_logs"}},
                ]
            )
        )


def execute(db, conn):

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE parameters_logs SET value = value * 1.1 WHERE parameter_id = %s",
            (param_id,),
        )
        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        collection.update_many(
            {"parameters_logs.parameter_id": param_id},
            {"$mul": {"parameters_logs.$[elem].value": 1.1}},
            array_filters=[{"elem.parameter_id": param_id}],
        )


def after(db, conn):
    if db == "pg":
        revert_update_postgres(conn, "parameters_logs", prev_param_logs, "id")
    elif db == "mysql":
        revert_update_mysql(conn, "parameters_logs", prev_param_logs, "id")
    elif db in ["mongo6", "mongo8"]:
        revert_update_mongo(conn, "users", prev_param_logs, "parameters_logs", param_id)

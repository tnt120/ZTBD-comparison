from scripts.test_utils.delete_revert import (
    revert_deletion_postgres,
    revert_deletion_mysql,
    revert_deletion_mongo,
)

prev_parameters = []


def before(db, conn):
    global prev_parameters

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()

        query = """
			SELECT p.*
			FROM parameters p
			WHERE NOT EXISTS (
				SELECT 1
				FROM parameters_logs pl
				WHERE pl.parameter_id = p.id
			);
		"""
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        prev_parameters = [dict(zip(columns, row)) for row in rows]

        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        parameters_collection = conn["parameters"]
        users_collection = conn["users"]
        used_parameter_ids = set()

        users_cursor = users_collection.find({}, {"parameters_logs.parameter_id": 1})
        for user in users_cursor:
            logs = user.get("parameters_logs", [])
            for log in logs:
                param_id = log.get("parameter_id")
                if param_id:
                    used_parameter_ids.add(param_id)
        unused_parameters_cursor = parameters_collection.find(
            {"_id": {"$nin": list(used_parameter_ids)}}
        )

        prev_parameters = list(unused_parameters_cursor)


def execute(db, conn):
    if db in ["pg", "mysql"]:
        cursor = conn.cursor()

        cursor.execute(
            f"""DELETE FROM parameters p WHERE NOT EXISTS (
				SELECT 1
				FROM parameters_logs pl
				WHERE pl.parameter_id = p.id
			);""",
        )

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        parameters_collection = conn["parameters"]

        parameter_ids = [p["_id"] for p in prev_parameters]

        parameters_collection.delete_many({"_id": {"$in": parameter_ids}})


def after(db, conn):
    if db == "pg":
        revert_deletion_postgres(conn, "parameters", prev_parameters)
    elif db == "mysql":
        revert_deletion_mysql(conn, "parameters", prev_parameters)
    elif db in ["mongo6", "mongo8"]:
        revert_deletion_mongo(conn, "parameters", prev_parameters)

from scripts.test_utils.delete_revert import (
    revert_deletion_postgres,
    revert_deletion_mysql,
    revert_deletion_mongo,
)

prev_drugs = []
user_ids = []

cutoff_date = "2024-12-31T23:59:59"


def before(db, conn):
    global prev_drugs, user_ids

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM drugs_logs WHERE created_at < %s", (cutoff_date,)
        )
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        prev_drugs = [dict(zip(columns, row)) for row in rows]

        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        users = collection.find({"drugs_logs.created_at": {"$lt": cutoff_date}})

        for user in users:
            matching_logs = [
                log
                for log in user.get("drugs_logs", [])
                if log.get("created_at") < cutoff_date
            ]
            if matching_logs:
                prev_drugs.extend(matching_logs)
                user_ids.extend([user["_id"]] * len(matching_logs))


def execute(db, conn):
    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        query = """
            DELETE FROM drugs_logs WHERE created_at < %s
        """
        cursor.execute(query, (cutoff_date,))

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        collection.update_many(
            {"drugs_logs.created_at": {"$lt": cutoff_date}},
            {"$pull": {"drugs_logs": {"created_at": {"$lt": cutoff_date}}}},
        )


def after(db, conn):
    if db == "pg":
        revert_deletion_postgres(conn, "drugs_logs", prev_drugs)
    elif db == "mysql":
        revert_deletion_mysql(conn, "drugs_logs", prev_drugs)
    elif db in ["mongo6", "mongo8"]:
        from collections import defaultdict

        user_logs = defaultdict(list)
        for log, uid in zip(prev_drugs, user_ids):
            user_logs[uid].append(log)

        for uid, logs in user_logs.items():
            revert_deletion_mongo(
                conn,
                "users",
                logs,
                "drugs_logs",
                uid,
            )

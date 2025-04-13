import random
from datetime import datetime
import uuid
from scripts.test_utils.insert_revert import (
    revert_insert_postgres,
    revert_insert_mysql,
    revert_insert_mongo,
)

log_ids = []
num_records = 1000


def execute(db, conn):
    log_ids = []
    user_id = "628ca258-261b-473f-9a1d-919e74b59341"
    parameter_id = "39828a6f-33ca-4740-a632-e9fd9c44fa9d"

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()

        for _ in range(num_records):
            log_id = str(uuid.uuid4())
            value = random.random()
            created_at = datetime.today().strftime("%Y-%m-%d")
            log_ids.append(log_id)

            query = """
                INSERT INTO parameters_logs (id, created_at, value, parameter_id, user_id)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(query, (log_id, created_at, value, parameter_id, user_id))

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]

        for _ in range(num_records):
            log_id = str(uuid.uuid4())
            value = random.random()
            created_at = datetime.today().strftime("%Y-%m-%d")
            log_ids.append(log_id)

            log_document = {
                "_id": log_id,
                "created_at": datetime.strptime(created_at, "%Y-%m-%d"),
                "value": value,
                "parameter_id": parameter_id,
                "user_id": user_id,
            }

            _ = collection.update_one(
                {"_id": user_id}, {"$push": {"parameters_logs": log_document}}
            )


def after(db, conn):
    if db == "pg":
        revert_insert_postgres(conn, "parameters_logs", log_ids)
    elif db == "mysql":
        revert_insert_mysql(conn, "parameters_logs", log_ids)
    elif db in ["mongo6", "mongo8"]:
        revert_insert_mongo(conn, "users", log_ids, "parameters_logs")

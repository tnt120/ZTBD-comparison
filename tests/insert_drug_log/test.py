import random
from datetime import datetime
import uuid
from scripts.test_utils.insert_revert import (
    revert_insert_postgres,
    revert_insert_mysql,
    revert_insert_mongo,
)


log_id = str(uuid.uuid4())
days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

def execute(db, conn):
    user_id = "628ca258-261b-473f-9a1d-919e74b59341"
    drug_id = 100002154
    taken_time = datetime.today().strftime("%H:%M:%S")
    time = datetime.today().strftime("%H:%M:%S")
    created_at = datetime.today().strftime("%Y-%m-%d")
    day = random.choice(days)

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        query = """
			INSERT INTO drugs_logs (id, created_at, day, taken_time, time, drug_id, user_id)
			VALUES (%s, %s, %s, %s, %s, %s, %s);
		"""
        cursor.execute(query, (log_id, created_at, day, taken_time, time, drug_id, user_id))

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]

        log_document = {
            "_id": log_id,
            "created_at": datetime.strptime(created_at, "%Y-%m-%d"),
            "day": day,
            "taken_time": taken_time,
            "time": time,
            "drug_id": drug_id,
            "user_id": user_id,
        }

        _ = collection.update_one(
            {"_id": user_id}, {"$push": {"drugs_logs": log_document}}
        )


def after(db, conn):
    if db == "pg":
        revert_insert_postgres(conn, "drugs_logs", [log_id])
    elif db == "mysql":
        revert_insert_mysql(conn, "drugs_logs", [log_id])
    elif db in ["mongo6", "mongo8"]:
        revert_insert_mongo(conn, "users", [log_id], "drugs_logs")

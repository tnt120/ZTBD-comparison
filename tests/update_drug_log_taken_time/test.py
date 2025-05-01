from scripts.test_utils.update_revert import (
    revert_update_postgres,
    revert_update_mysql,
    revert_update_mongo,
)
from datetime import datetime
import json
from bson import json_util
import time
import copy

prev_drug_logs = []
test_taken_time = None


def before(db, conn):
    global prev_drug_logs, test_taken_time

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drugs_logs LIMIT 1")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        prev_drug_logs = [dict(zip(columns, row)) for row in rows]

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        result = collection.aggregate([
            {"$unwind": "$drugs_logs"},
            {"$limit": 1}
        ])
        doc = next(result, None)

        if doc:
            drug_log_copy = json.loads(json_util.dumps(doc["drugs_logs"]))
            prev_drug_logs = [{
                "_id": doc["_id"],
                "drugs_logs": drug_log_copy
            }]
            test_taken_time = copy.deepcopy(drug_log_copy["taken_time"])

def execute(db, conn):
    global prev_drug_logs
    taken_time = datetime.today().strftime("%H:%M:%S")

    if db in ["pg", "mysql"]:
        drug_log_id = prev_drug_logs[0]["id"]
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE drugs_logs SET taken_time = %s WHERE id = %s",
            (taken_time, drug_log_id),
        )
        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        drug_log_id = prev_drug_logs[0]["drugs_logs"]["_id"]
        collection = conn["users"]

        collection.update_many(
            {"drugs_logs._id": drug_log_id},
            {"$set": {"drugs_logs.$[elem].taken_time": taken_time}},
            array_filters=[{"elem._id": drug_log_id}]
        )
    

def after(db, conn):
    global prev_drug_logs, test_taken_time
    if db == "pg":
        revert_update_postgres(conn, "drugs_logs", prev_drug_logs, "id")
    elif db == "mysql":
        revert_update_mysql(conn, "drugs_logs", prev_drug_logs, "id")
    elif db in ["mongo6", "mongo8"]:
        prev_drug_logs[0]["drugs_logs"]["taken_time"] = test_taken_time
        revert_update_mongo(
            conn,
            "users",
            prev_drug_logs,
            "drugs_logs",
            prev_drug_logs[0]["drugs_logs"]["_id"]
        )


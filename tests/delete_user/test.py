from scripts.test_utils.delete_revert import (
    revert_deletion_postgres,
    revert_deletion_mysql,
    revert_deletion_mongo,
)

user_id = "bb82a87b-4876-4214-8d3c-b6abcbfe6066"
prev_user = None
prev_user_drugs = []
prev_parameters_logs = []
prev_drugs_logs = []
prev_drug_dose_day = []
prev_drug_dose_time = []
user_drug_ids = []


def before(db, conn):
    global prev_user, prev_user_drugs, prev_parameters_logs, prev_drugs_logs, prev_drug_dose_day, prev_drug_dose_time, user_drug_ids

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()

        def fetch_all(query, params=None):
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            cols = [desc[0] for desc in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            cols = [desc[0] for desc in cursor.description]
            prev_user = dict(zip(cols, row))

        prev_user_drugs = fetch_all("SELECT * FROM user_drugs WHERE user_id = %s", (user_id,))
        user_drug_ids = [ud["id"] for ud in prev_user_drugs]

        if user_drug_ids:
            placeholders = ", ".join(["%s"] * len(user_drug_ids))
            prev_drug_dose_day = fetch_all(f"SELECT * FROM drug_dose_day WHERE user_drug_id IN ({placeholders})", user_drug_ids)
            prev_drug_dose_time = fetch_all(f"SELECT * FROM drug_dose_time WHERE user_drug_id IN ({placeholders})", user_drug_ids)

        prev_parameters_logs = fetch_all("SELECT * FROM parameters_logs WHERE user_id = %s", (user_id,))
        prev_drugs_logs = fetch_all("SELECT * FROM drugs_logs WHERE user_id = %s", (user_id,))

        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        user = conn["users"].find_one({"_id": user_id})
        if not user:
            return

        prev_user = user.copy()
        prev_user_drugs = []

        for ud in user.get("user_drugs", []):
            ud_copy = ud.copy()
            ud_copy["_days"] = ud_copy.pop("days", [])
            ud_copy["_times"] = ud_copy.pop("times", [])
            prev_user_drugs.append(ud_copy)

        prev_parameters_logs = user.get("parameters_logs", [])
        prev_drugs_logs = user.get("drugs_logs", [])


def execute(db, conn):
    if db in ["pg", "mysql"]:
        cursor = conn.cursor()

        if user_drug_ids:
            placeholders = ", ".join(["%s"] * len(user_drug_ids))
            cursor.execute(f"DELETE FROM drug_dose_time WHERE user_drug_id IN ({placeholders})", user_drug_ids)
            cursor.execute(f"DELETE FROM drug_dose_day WHERE user_drug_id IN ({placeholders})", user_drug_ids)

        cursor.execute("DELETE FROM user_drugs WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM parameters_logs WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM drugs_logs WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        conn["users"].delete_one({"_id": user_id})


def after(db, conn):
    if prev_user is None:
        print("No user to restore.")
        return

    if db == "pg":
        revert_deletion_postgres(conn, "users", [prev_user])
        if prev_user_drugs:
            revert_deletion_postgres(conn, "user_drugs", prev_user_drugs)
        if prev_drug_dose_day:
            revert_deletion_postgres(conn, "drug_dose_day", prev_drug_dose_day)
        if prev_drug_dose_time:
            revert_deletion_postgres(conn, "drug_dose_time", prev_drug_dose_time)
        if prev_parameters_logs:
            revert_deletion_postgres(conn, "parameters_logs", prev_parameters_logs)
        if prev_drugs_logs:
            revert_deletion_postgres(conn, "drugs_logs", prev_drugs_logs)

    elif db == "mysql":
        revert_deletion_mysql(conn, "users", [prev_user])
        if prev_user_drugs:
            revert_deletion_mysql(conn, "user_drugs", prev_user_drugs)
        if prev_drug_dose_day:
            revert_deletion_mysql(conn, "drug_dose_day", prev_drug_dose_day)
        if prev_drug_dose_time:
            revert_deletion_mysql(conn, "drug_dose_time", prev_drug_dose_time)
        if prev_parameters_logs:
            revert_deletion_mysql(conn, "parameters_logs", prev_parameters_logs)
        if prev_drugs_logs:
            revert_deletion_mysql(conn, "drugs_logs", prev_drugs_logs)

    elif db in ["mongo6", "mongo8"]:
        user_doc = prev_user.copy()
        user_doc["user_drugs"] = []

        for ud in prev_user_drugs:
            restored_ud = ud.copy()
            restored_ud["days"] = ud.get("_days", [])
            restored_ud["times"] = ud.get("_times", [])
            user_doc["user_drugs"].append(restored_ud)

        if prev_parameters_logs:
            user_doc["parameters_logs"] = prev_parameters_logs

        if prev_drugs_logs:
            user_doc["drugs_logs"] = prev_drugs_logs

        conn["users"].insert_one(user_doc)

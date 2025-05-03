from scripts.test_utils.delete_revert import (
    revert_deletion_postgres,
    revert_deletion_mysql,
    revert_deletion_mongo,
)

drug_id = 100415850
prev_drug = None
prev_drug_packs = []
prev_user_drugs = []
prev_drug_dose_day = []
prev_drug_dose_time = []
prev_drugs_logs = []
affected_user_ids = set()
user_drug_ids = []


def before(db, conn):
    global prev_drug, prev_drug_packs, prev_user_drugs, prev_drug_dose_day, prev_drug_dose_time, prev_drugs_logs, affected_user_ids, user_drug_ids

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()

        def fetch_all(query, params=None):
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            cols = [desc[0] for desc in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM drugs WHERE id = %s", (drug_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            prev_drug = dict(zip(columns, row))

        prev_drug_packs = fetch_all("SELECT * FROM drug_packs WHERE drug_id = %s", (drug_id,))
        prev_user_drugs = fetch_all("SELECT * FROM user_drugs WHERE drug_id = %s", (drug_id,))
        user_drug_ids = [row["id"] for row in prev_user_drugs]

        if user_drug_ids:
            placeholders = ", ".join(["%s"] * len(user_drug_ids))
            prev_drug_dose_day = fetch_all(f"SELECT * FROM drug_dose_day WHERE user_drug_id IN ({placeholders})", user_drug_ids)
            prev_drug_dose_time = fetch_all(f"SELECT * FROM drug_dose_time WHERE user_drug_id IN ({placeholders})", user_drug_ids)
        else:
            prev_drug_dose_day = []
            prev_drug_dose_time = []

        prev_drugs_logs = fetch_all("SELECT * FROM drugs_logs WHERE drug_id = %s", (drug_id,))
        affected_user_ids = {row["user_id"] for row in prev_user_drugs}

        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        prev_drug = conn["drugs"].find_one({"_id": drug_id})
        prev_drug_packs = prev_drug.get("packs", []) if prev_drug else []

        prev_user_drugs = []
        for user in conn["users"].find({"user_drugs.drug_id": drug_id}):
            for ud in user.get("user_drugs", []):
                if ud["drug_id"] == drug_id:
                    ud_copy = ud.copy()
                    ud_copy["_user_id"] = user["_id"]
                    prev_user_drugs.append(ud_copy)
                    affected_user_ids.add(user["_id"])


def execute(db, conn):
    if db in ["pg", "mysql"]:
        cursor = conn.cursor()

        if user_drug_ids:
            placeholders = ", ".join(["%s"] * len(user_drug_ids))
            cursor.execute(f"DELETE FROM drug_dose_time WHERE user_drug_id IN ({placeholders})", user_drug_ids)
            cursor.execute(f"DELETE FROM drug_dose_day WHERE user_drug_id IN ({placeholders})", user_drug_ids)

        cursor.execute("DELETE FROM user_drugs WHERE drug_id = %s", (drug_id,))
        cursor.execute("DELETE FROM drug_packs WHERE drug_id = %s", (drug_id,))
        cursor.execute("DELETE FROM drugs_logs WHERE drug_id = %s", (drug_id,))
        cursor.execute("DELETE FROM drugs WHERE id = %s", (drug_id,))

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        conn["drugs"].delete_one({"_id": drug_id})

        for user_id in affected_user_ids:
            conn["users"].update_one(
                {"_id": user_id},
                {"$pull": {"user_drugs": {"drug_id": drug_id}}}
            )


def after(db, conn):
    if not prev_drug:
        print("No drug to restore.")
        return

    if db == "pg":
        revert_deletion_postgres(conn, "drugs", [prev_drug])
        if prev_drug_packs:
            revert_deletion_postgres(conn, "drug_packs", prev_drug_packs)
        if prev_user_drugs:
            revert_deletion_postgres(conn, "user_drugs", prev_user_drugs)
        if prev_drug_dose_day:
            revert_deletion_postgres(conn, "drug_dose_day", prev_drug_dose_day)
        if prev_drug_dose_time:
            revert_deletion_postgres(conn, "drug_dose_time", prev_drug_dose_time)
        if prev_drugs_logs:
            revert_deletion_postgres(conn, "drugs_logs", prev_drugs_logs)

    elif db == "mysql":
        revert_deletion_mysql(conn, "drugs", [prev_drug])
        if prev_drug_packs:
            revert_deletion_mysql(conn, "drug_packs", prev_drug_packs)
        if prev_user_drugs:
            revert_deletion_mysql(conn, "user_drugs", prev_user_drugs)
        if prev_drug_dose_day:
            revert_deletion_mysql(conn, "drug_dose_day", prev_drug_dose_day)
        if prev_drug_dose_time:
            revert_deletion_mysql(conn, "drug_dose_time", prev_drug_dose_time)
        if prev_drugs_logs:
            revert_deletion_mysql(conn, "drugs_logs", prev_drugs_logs)

    elif db in ["mongo6", "mongo8"]:
        conn["drugs"].insert_one(prev_drug)
        for ud in prev_user_drugs:
            user_id = ud.pop("_user_id")
            conn["users"].update_one(
                {"_id": user_id},
                {"$push": {"user_drugs": ud}},
                upsert=True
            )

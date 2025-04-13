from scripts.test_utils.update_revert import (
    revert_update_postgres,
    revert_update_mysql,
    revert_update_mongo,
)

user_drug_id = "c91f8d81-14d2-4f82-87f9-34ba8a751c08"
prev_dose_times = None


def before(db, conn):
    global prev_dose_times

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM drug_dose_time WHERE user_drug_id = %s", (user_drug_id,)
        )
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        prev_dose_times = [dict(zip(columns, row)) for row in rows]
    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]

        user = collection.find_one({"user_drugs.id": user_drug_id}, {"user_drugs.$": 1})

        if user and "user_drugs" in user:
            for ud in user["user_drugs"]:
                if ud.get("id") == user_drug_id:
                    prev_dose_times = ud.get("times", [])
                    break


def execute(db, conn):

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        first_time_rec = prev_dose_times[0]
        second_time_rec = prev_dose_times[1]

        cursor.execute(
            "UPDATE drug_dose_time SET dose_time = %s WHERE id = %s",
            ("19:00:00", first_time_rec["id"]),
        )

        cursor.execute(
            "UPDATE drug_dose_time SET dose_time = %s WHERE id = %s",
            ("7:00:00", second_time_rec["id"]),
        )

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]

        for dose_time in prev_dose_times:
            collection.update_one(
                {"user_drugs.id": user_drug_id},
                {"$set": {"user_drugs.$[elem].times.$[timeElem]": dose_time}},
                array_filters=[
                    {"elem.id": user_drug_id},
                    {"timeElem": dose_time},
                ],
            )


def after(db, conn):
    if db == "pg":
        revert_update_postgres(conn, "drug_dose_time", prev_dose_times, "id")
    elif db == "mysql":
        revert_update_mysql(conn, "drug_dose_time", prev_dose_times, "id")
    elif db in ["mongo6", "mongo8"]:
        revert_update_mongo(
            conn, "users", prev_dose_times, "users_drugs.times", user_drug_id
        )

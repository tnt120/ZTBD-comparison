from scripts.test_utils.update_revert import (
    revert_update_postgres,
    revert_update_mysql,
    revert_update_mongo,
)

user_drug_id = "a7e8d53f-7405-4efa-8f9c-82876ad160a7"
prev_user_drug = None


def before(db, conn):
    global prev_user_drug

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_drugs WHERE id = %s", (user_drug_id,))
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        prev_user_drug = dict(zip(columns, row))
    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        user = collection.find_one({"user_drugs.id": user_drug_id})

        prev_user_drug = next(
            (drug for drug in user.get("user_drugs", []) if drug["id"] == user_drug_id),
            None,
        )


def execute(db, conn):
    new_dosage = 5

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE user_drugs SET dose_size = %s WHERE id = %s",
            (new_dosage, user_drug_id),
        )
        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        collection.update_one(
            {"user_drugs.id": user_drug_id},
            {"$set": {"user_drugs.$.dose_size": new_dosage}},
        )


def after(db, conn):
    if db == "pg":
        revert_update_postgres(conn, "user_drugs", [prev_user_drug], "id")
    elif db == "mysql":
        revert_update_mysql(conn, "user_drugs", [prev_user_drug], "id")
    elif db in ["mongo6", "mongo8"]:
        revert_update_mongo(conn, "users", prev_user_drug, "users_drugs", user_drug_id)

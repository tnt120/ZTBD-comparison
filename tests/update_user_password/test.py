from faker import Faker
from scripts.test_utils.update_revert import (
    revert_update_postgres,
    revert_update_mysql,
    revert_update_mongo,
)

fake = Faker()
user_id = "cdd1d5a9-82f3-47ce-8f11-cff5b9b39111"
prev_user = None


def before(db, conn):
    global prev_user

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        prev_user = dict(zip(columns, row))
    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        user = collection.find_one({"_id": user_id})
        prev_user = user


def execute(db, conn):

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        new_password = fake.password()
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s", (new_password, user_id)
        )
        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        new_password = fake.password()
        collection.update_one({"_id": user_id}, {"$set": {"password": new_password}})


def after(db, conn):
    if db == "pg":
        revert_update_postgres(conn, "users", [prev_user], "id")
    elif db == "mysql":
        revert_update_mysql(conn, "users", [prev_user], "id")
    elif db in ["mongo6", "mongo8"]:
        revert_update_mongo(conn, "users", [prev_user])

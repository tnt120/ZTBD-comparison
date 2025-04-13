import random
from datetime import datetime
import uuid
from faker import Faker
from scripts.test_utils.insert_revert import (
    revert_insert_postgres,
    revert_insert_mysql,
    revert_insert_mongo,
)

fake = Faker()

users = []
num_records = 20


def generate_random_user_data():
    for _ in range(num_records):
        user_id = str(uuid.uuid4())
        email = fake.email()
        name = fake.first_name()
        surname = fake.last_name()
        password = fake.password()
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime(
            "%Y-%m-%d"
        )
        creation_date = datetime.today().strftime("%Y-%m-%d")
        sex = random.choice(["MALE", "FEMALE", "OTHER"])

        users.append(
            {
                "id": user_id,
                "email": email,
                "name": name,
                "surname": surname,
                "password": password,
                "birth_date": birth_date,
                "creation_date": creation_date,
                "sex": sex,
            }
        )


def before(db, conn):
    generate_random_user_data()


def execute(db, conn):

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()

        for user_data in users:

            query = """
				INSERT INTO users (id, email, name, surname, password, birth_date, creation_date, sex)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
			"""
            cursor.execute(
                query,
                (
                    user_data["id"],
                    user_data["email"],
                    user_data["name"],
                    user_data["surname"],
                    user_data["password"],
                    user_data["birth_date"],
                    user_data["creation_date"],
                    user_data["sex"],
                ),
            )

        conn.commit()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]

        for user_data in users:

            user_document = {
                "_id": user_data["id"],
                "email": user_data["email"],
                "name": user_data["name"],
                "surname": user_data["surname"],
                "password": user_data["password"],
                "birth_date": datetime.strptime(user_data["birth_date"], "%Y-%m-%d"),
                "creation_date": datetime.strptime(
                    user_data["creation_date"], "%Y-%m-%d"
                ),
                "sex": user_data["sex"],
            }

            collection.insert_one(user_document)


def after(db, conn):
    if db == "pg":
        revert_insert_postgres(conn, "users", [u["id"] for u in users])
    elif db == "mysql":
        revert_insert_mysql(conn, "users", [u["id"] for u in users])
    elif db in ["mongo6", "mongo8"]:
        revert_insert_mongo(conn, "users", [u["id"] for u in users])

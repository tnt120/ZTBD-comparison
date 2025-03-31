import psycopg2
import mysql.connector
from pymongo import MongoClient, UpdateOne
import random
from datetime import datetime, timedelta, time as time_obj
from uuid import uuid4
from tqdm import tqdm
from time import time

POSTGRES_SETTINGS = {
    'host': 'localhost',
    'port': '5433',
    'dbname': 'postgres_ZTBD',
    'user': 'postgres',
    'password': 'postgres'
}

MYSQL_SETTINGS = {
    'host': 'localhost',
    'port': 3307,
    'database': 'mysql_ZTBD',
    'user': 'root',
    'password': 'mysql'
}

MONGO_URI1 = "mongodb://mongo:mongo@localhost:27017/"
MONGO_URI2 = "mongodb://mongo:mongo@localhost:27018/"
DB_NAME = "test"
COLLECTION_NAME = "users"

NUM_RECORDS = 50_000

WEEKDAYS = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']

def random_datetime(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

pg_conn = psycopg2.connect(**POSTGRES_SETTINGS)
pg_cursor = pg_conn.cursor()

pg_cursor.execute("SELECT user_id, drug_id FROM user_drugs")
user_drugs = pg_cursor.fetchall()

print(f"[PostgreSQL] Znaleziono {len(user_drugs)} par (user_id, drug_id)")

records = []
now = datetime.now()
start_date = now - timedelta(days=180)

print(f"[INFO] Generowanie {NUM_RECORDS} logów...")
for _ in tqdm(range(NUM_RECORDS), desc="Generowanie"):
    user_id, drug_id = random.choice(user_drugs)
    created_at = random_datetime(start_date, now)
    day = WEEKDAYS[created_at.weekday()]
    planned_hour = random.randint(6, 22)
    planned_minute = random.choice([0, 15, 30, 45])
    planned_time = time_obj(planned_hour, planned_minute)

    taken_time_dt = datetime.combine(created_at.date(), planned_time) + timedelta(minutes=random.randint(-10, 10))
    taken_time = taken_time_dt.time()

    records.append({
        "id": str(uuid4()),
        "created_at": created_at,
        "day": day,
        "taken_time": taken_time,
        "time": planned_time,
        "drug_id": drug_id,
        "user_id": user_id
    })

print("\n[PostgreSQL] Wstawianie danych...")
start_pg = time()
batch = []
for rec in tqdm(records, desc="PostgreSQL"):
    batch.append((rec['id'], rec['created_at'], rec['day'], rec['taken_time'], rec['time'], rec['drug_id'], rec['user_id']))
    if len(batch) >= 10000:
        args_str = ','.join(pg_cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s)", b).decode('utf-8') for b in batch)
        pg_cursor.execute("INSERT INTO drugs_logs (id, created_at, day, taken_time, time, drug_id, user_id) VALUES " + args_str)
        pg_conn.commit()
        batch = []
if batch:
    args_str = ','.join(pg_cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s)", b).decode('utf-8') for b in batch)
    pg_cursor.execute("INSERT INTO drugs_logs (id, created_at, day, taken_time, time, drug_id, user_id) VALUES " + args_str)
    pg_conn.commit()
end_pg = time()
pg_cursor.close()
pg_conn.close()

print("\n[MySQL] Wstawianie danych...")
mysql_conn = mysql.connector.connect(**MYSQL_SETTINGS)
mysql_cursor = mysql_conn.cursor()
start_mysql = time()
batch = []
sql = "INSERT INTO drugs_logs (id, created_at, day, taken_time, time, drug_id, user_id) VALUES (%s,%s,%s,%s,%s,%s,%s)"
for rec in tqdm(records, desc="MySQL"):
    batch.append((rec['id'], rec['created_at'], rec['day'], rec['taken_time'], rec['time'], rec['drug_id'], rec['user_id']))
    if len(batch) >= 10000:
        mysql_cursor.executemany(sql, batch)
        mysql_conn.commit()
        batch = []
if batch:
    mysql_cursor.executemany(sql, batch)
    mysql_conn.commit()
end_mysql = time()
mysql_cursor.close()
mysql_conn.close()

def insert_to_mongo(uri, label):
    print(f"\n[{label}] Wstawianie danych...")
    client = MongoClient(uri)
    coll = client[DB_NAME][COLLECTION_NAME]
    bulk_ops = {}
    for rec in tqdm(records, desc=f"{label} przygotowanie"):
        entry = {
            "drug_id": rec['drug_id'],
            "created_at": rec['created_at'],
            "day": rec['day'],
            "taken_time": rec['taken_time'].strftime("%H:%M"),
            "time": rec['time'].strftime("%H:%M")
        }
        if rec['user_id'] not in bulk_ops:
            bulk_ops[rec['user_id']] = []
        bulk_ops[rec['user_id']].append(entry)

    for user_id, logs in tqdm(bulk_ops.items(), desc=f"{label} zapisy"):
        updates = [UpdateOne({"_id": user_id}, {"$push": {"drugs_logs": log}}) for log in logs]
        for i in range(0, len(updates), 1000):
            coll.bulk_write(updates[i:i + 1000])

start_mongo = time()
insert_to_mongo(MONGO_URI1, "MongoDB 1")
insert_to_mongo(MONGO_URI2, "MongoDB 2")
end_mongo = time()

print("\n--- CZAS WYKONANIA ---")
print(f"PostgreSQL: {end_pg - start_pg:.2f} sek")
print(f"MySQL:      {end_mysql - start_mysql:.2f} sek")
print(f"MongoDB:    {end_mongo - start_mongo:.2f} sek")

import psycopg2
import mysql.connector
from pymongo import MongoClient, UpdateOne
from uuid import uuid4
from datetime import datetime, timedelta, time
from tqdm import tqdm
import random
from time import time as t_time

# --- Konfiguracje ---
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
MONGO_DB = "test"
MONGO_COLL = "users"

WEEKDAYS = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']

pg_conn = psycopg2.connect(**POSTGRES_SETTINGS)
pg_cursor = pg_conn.cursor()
pg_cursor.execute("SELECT id FROM users")
user_ids = [row[0] for row in pg_cursor.fetchall()]

pg_cursor.execute("SELECT id FROM drugs")
drug_ids = [row[0] for row in pg_cursor.fetchall()]

print(f"[PostgreSQL] Użytkownicy: {len(user_ids)}, Leki: {len(drug_ids)}")

print("\n[Generowanie user_drugs]")

user_drugs = []
for user_id in tqdm(user_ids):
    selected = random.sample(drug_ids, random.randint(2, 5))
    for drug_id in selected:
        user_drug_id = str(uuid4())
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=random.randint(30, 180))
        dose_days = random.sample(WEEKDAYS, random.randint(1, 7))
        dose_times = [time(random.randint(6, 22), random.choice([0, 15, 30, 45])) for _ in range(random.randint(1, 5))]

        user_drugs.append({
            "id": user_drug_id,
            "amount": random.randint(10, 100),
            "dose_size": random.randint(1, 3),
            "end_date": end_date,
            "priority": random.choice(["LOW", "HIGH"]),
            "start_date": start_date,
            "drug_id": drug_id,
            "user_id": user_id,
            "days": dose_days,
            "times": dose_times
        })

print("\n[PostgreSQL] Insert danych...")
start_pg = t_time()
batch = []
for row in tqdm(user_drugs):
    batch.append((
        row["id"], row["amount"], row["dose_size"], row["end_date"],
        row["priority"], row["start_date"], row["drug_id"], row["user_id"]
    ))
    if len(batch) >= 5000:
        args_str = ",".join(pg_cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s)", b).decode() for b in batch)
        pg_cursor.execute("INSERT INTO user_drugs (id, amount, dose_size, end_date, priority, start_date, drug_id, user_id) VALUES " + args_str)
        pg_conn.commit()
        batch = []
if batch:
    args_str = ",".join(pg_cursor.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s)", b).decode() for b in batch)
    pg_cursor.execute("INSERT INTO user_drugs (id, amount, dose_size, end_date, priority, start_date, drug_id, user_id) VALUES " + args_str)
    pg_conn.commit()

batch_day = []
for row in user_drugs:
    for day in row["days"]:
        batch_day.append((str(uuid4()), day, row["id"]))
        if len(batch_day) >= 5000:
            args_str = ",".join(pg_cursor.mogrify("(%s,%s,%s)", b).decode() for b in batch_day)
            pg_cursor.execute("INSERT INTO drug_dose_day (id, day, user_drug_id) VALUES " + args_str)
            pg_conn.commit()
            batch_day = []
if batch_day:
    args_str = ",".join(pg_cursor.mogrify("(%s,%s,%s)", b).decode() for b in batch_day)
    pg_cursor.execute("INSERT INTO drug_dose_day (id, day, user_drug_id) VALUES " + args_str)
    pg_conn.commit()

batch_time = []
for row in user_drugs:
    for t in row["times"]:
        batch_time.append((str(uuid4()), t, row["id"]))
        if len(batch_time) >= 5000:
            args_str = ",".join(pg_cursor.mogrify("(%s,%s,%s)", b).decode() for b in batch_time)
            pg_cursor.execute("INSERT INTO drug_dose_time (id, dose_time, user_drug_id) VALUES " + args_str)
            pg_conn.commit()
            batch_time = []
if batch_time:
    args_str = ",".join(pg_cursor.mogrify("(%s,%s,%s)", b).decode() for b in batch_time)
    pg_cursor.execute("INSERT INTO drug_dose_time (id, dose_time, user_drug_id) VALUES " + args_str)
    pg_conn.commit()

pg_cursor.close()
pg_conn.close()
end_pg = t_time()

print("\n[MySQL] Insert danych...")
mysql_conn = mysql.connector.connect(**MYSQL_SETTINGS)
mysql_cursor = mysql_conn.cursor()
start_mysql = t_time()
batch = []
sql = "INSERT INTO user_drugs (id, amount, dose_size, end_date, priority, start_date, drug_id, user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
for row in tqdm(user_drugs):
    batch.append((
        row["id"], row["amount"], row["dose_size"], row["end_date"],
        row["priority"], row["start_date"], row["drug_id"], row["user_id"]
    ))
    if len(batch) >= 5000:
        mysql_cursor.executemany(sql, batch)
        mysql_conn.commit()
        batch = []
if batch:
    mysql_cursor.executemany(sql, batch)
    mysql_conn.commit()
mysql_cursor.close()
mysql_conn.close()
end_mysql = t_time()

def mongo_insert(uri, label):
    print(f"\n[{label}] Insert danych...")
    client = MongoClient(uri)
    coll = client[MONGO_DB][MONGO_COLL]

    bulk_ops = {}
    for row in tqdm(user_drugs, desc=f"{label}"):
        entry = {
            "id": row["id"],
            "amount": row["amount"],
            "dose_size": row["dose_size"],
            "end_date": datetime.combine(row["end_date"], datetime.min.time()),
            "priority": row["priority"],
            "start_date": datetime.combine(row["start_date"], datetime.min.time()),
            "drug_id": row["drug_id"],
            "days": row["days"],
            "times": [t.strftime("%H:%M") for t in row["times"]]
        }
        if row["user_id"] not in bulk_ops:
            bulk_ops[row["user_id"]] = []
        bulk_ops[row["user_id"]].append(entry)

    for user_id, entries in tqdm(bulk_ops.items(), desc=f"{label} updates"):
        updates = [UpdateOne({"_id": user_id}, {"$push": {"user_drugs": entry}}) for entry in entries]
        for i in range(0, len(updates), 1000):
            coll.bulk_write(updates[i:i + 1000])

mongo_insert(MONGO_URI1, "MongoDB 1")
mongo_insert(MONGO_URI2, "MongoDB 2")

print("\n--- CZAS WYKONANIA ---")
print(f"PostgreSQL: {end_pg - start_pg:.2f}s")
print(f"MySQL:      {end_mysql - start_mysql:.2f}s")
print("MongoDB:    Zrobione (osobne czasy nie mierzone osobno)")

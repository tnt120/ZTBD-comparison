import psycopg2
import mysql.connector
from pymongo import MongoClient, UpdateOne
import random
from datetime import datetime, timedelta
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

MONGO_URI = "mongodb://mongo:mongo@localhost:27017/"
DB_NAME = "test"
COLLECTION_NAME = "users"

MONGO_URI2 = "mongodb://mongo:mongo@localhost:27018/"
DB_NAME2 = "test"
COLLECTION_NAME2 = "users"

NUM_RECORDS = 500_000

def random_datetime(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

pg_conn = psycopg2.connect(**POSTGRES_SETTINGS)
pg_cursor = pg_conn.cursor()

pg_cursor.execute("SELECT id FROM users")
user_ids = [row[0] for row in pg_cursor.fetchall()]

pg_cursor.execute("SELECT id, min_value, max_value FROM parameters")
parameters = pg_cursor.fetchall()

print(f"[PostgreSQL] Użytkownicy: {len(user_ids)}, Parametry: {len(parameters)}")

records = []
now = datetime.now()
start_date = now - timedelta(days=180)

for _ in tqdm(range(NUM_RECORDS), desc="Generowanie danych"):
    user_id = random.choice(user_ids)
    param_id, min_val, max_val = random.choice(parameters)
    value = round(random.uniform(min_val, max_val))
    created_at = random_datetime(start_date, now)
    records.append({
        "id": str(uuid4()),
        "created_at": created_at,
        "value": value,
        "parameter_id": param_id,
        "user_id": user_id
    })

print("\n[PostgreSQL] Wstawianie danych...")
start_pg = time()
batch = []
for rec in tqdm(records, desc="PostgreSQL"):
    batch.append((rec['id'], rec['created_at'], rec['value'], rec['parameter_id'], rec['user_id']))
    if len(batch) >= 10000:
        args_str = ','.join(pg_cursor.mogrify("(%s,%s,%s,%s,%s)", b).decode('utf-8') for b in batch)
        pg_cursor.execute("INSERT INTO parameters_logs (id, created_at, value, parameter_id, user_id) VALUES " + args_str)
        pg_conn.commit()
        batch = []
if batch:
    args_str = ','.join(pg_cursor.mogrify("(%s,%s,%s,%s,%s)", b).decode('utf-8') for b in batch)
    pg_cursor.execute("INSERT INTO parameters_logs (id, created_at, value, parameter_id, user_id) VALUES " + args_str)
    pg_conn.commit()
end_pg = time()
pg_cursor.close()
pg_conn.close()

print("\n[MySQL] Wstawianie danych...")
mysql_conn = mysql.connector.connect(**MYSQL_SETTINGS)
mysql_cursor = mysql_conn.cursor()
start_mysql = time()
batch = []
for rec in tqdm(records, desc="MySQL"):
    batch.append((rec['id'], rec['created_at'], rec['value'], rec['parameter_id'], rec['user_id']))
    if len(batch) >= 10000:
        sql = "INSERT INTO parameters_logs (id, created_at, value, parameter_id, user_id) VALUES (%s,%s,%s,%s,%s)"
        mysql_cursor.executemany(sql, batch)
        mysql_conn.commit()
        batch = []
if batch:
    mysql_cursor.executemany(sql, batch)
    mysql_conn.commit()
end_mysql = time()
mysql_cursor.close()
mysql_conn.close()

print("\n[MongoDB] Wstawianie danych...")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[DB_NAME]
users_coll = mongo_db[COLLECTION_NAME]
start_mongo = time()

bulk_ops = {}
for rec in tqdm(records, desc="MongoDB"):
    op = {
        "$push": {
            "parameters_logs": {
                "parameter_id": rec['parameter_id'],
                "value": rec['value'],
                "created_at": rec['created_at']
            }
        }
    }
    if rec['user_id'] not in bulk_ops:
        bulk_ops[rec['user_id']] = []
    bulk_ops[rec['user_id']].append(op)

for user_id, ops in tqdm(bulk_ops.items(), desc="MongoDB User Inserts"):
    updates = [UpdateOne({"_id": user_id},  op) for op in ops]
    for i in range(0, len(updates), 1000):
        users_coll.bulk_write(updates[i:i + 1000])
end_mongo = time()

print("\n[MongoDB] Wstawianie danych...")
mongo_client = MongoClient(MONGO_URI2)
mongo_db = mongo_client[DB_NAME2]
users_coll = mongo_db[COLLECTION_NAME2]
start_mongo = time()

bulk_ops = {}
for rec in tqdm(records, desc="MongoDB"):
    op = {
        "$push": {
            "parameters_logs": {
                "parameter_id": rec['parameter_id'],
                "value": rec['value'],
                "created_at": rec['created_at']
            }
        }
    }
    if rec['user_id'] not in bulk_ops:
        bulk_ops[rec['user_id']] = []
    bulk_ops[rec['user_id']].append(op)

for user_id, ops in tqdm(bulk_ops.items(), desc="MongoDB User Inserts"):
    updates = [UpdateOne({"_id": user_id},  op) for op in ops]
    for i in range(0, len(updates), 1000):
        users_coll.bulk_write(updates[i:i + 1000])
end_mongo = time()

print("\n--- CZAS INSERTU ---")
print(f"PostgreSQL: {end_pg - start_pg:.2f} sek")
print(f"MySQL:      {end_mysql - start_mysql:.2f} sek")
print(f"MongoDB:    {end_mongo - start_mongo:.2f} sek")

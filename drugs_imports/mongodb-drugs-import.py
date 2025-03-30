import json
from pymongo import MongoClient

MONGO_URI = "mongodb://mongo:mongo@localhost:27018/"
DB_NAME = "test"
COLLECTION_NAME = "users"
JSON_FILE = "users.json"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

with open(JSON_FILE, "r", encoding="utf-8") as f:
    for line in f:
        doc = json.loads(line)
        collection.insert_one(doc)

print("✅ Import zakończony!")

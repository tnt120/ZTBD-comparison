import sys
import os
import pymongo
import json
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='MongoDB Schema Application Script')

    parser.add_argument('--target', type=str, default='all', help='mongo6, mongo8 or all(default)')

    return parser.parse_args()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from env import MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB
from env import MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB
from utils import print_colored

FILE_PATH = 'source/mongo.json'


def apply_mongo_schema(host, port, user, password, db):
	client = pymongo.MongoClient(
		host,
		port=int(port),
		username=user,
		password=password
	)
      
	db =  client[db]

	with open(FILE_PATH, 'r') as file:
		schema_operations = json.load(file)

		for operation in schema_operations:
			collection_name = operation['createCollection']
			validator = operation.get('validator', {})

			if collection_name not in db.list_collection_names():
				db.create_collection(collection_name, validator=validator)
			else:
				print_colored(f"Collection '{collection_name}' already exists.", "RED")

	client.close()

if __name__ == "__main__":
	args = parse_args()
	
	if args.target == "all" or args.target == "mongo6":
		try:
			apply_mongo_schema(MONGO6_HOST, MONGO6_PORT, MONGO6_USER, MONGO6_PASSWORD, MONGO6_DB)
			print_colored(f"MongoDB 6 schema applied successfully.", "GREEN")
		except:
			print_colored("Failed to apply mongo6", "RED")
	
	if args.target == "all" or args.target == "mongo8":
		try:
			apply_mongo_schema(MONGO8_HOST, MONGO8_PORT, MONGO8_USER, MONGO8_PASSWORD, MONGO8_DB)
			print_colored(f"MongoDB 8 schema applied successfully.", "GREEN")
		except:
			print_colored("Failed to apply mongo8", "RED")

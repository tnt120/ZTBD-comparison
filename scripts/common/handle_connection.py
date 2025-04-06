import sys
import os

import psycopg2
import mysql.connector
import pymongo

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from env import (
	POSTGRES_HOST,
	POSTGRES_PORT,
	POSTGRES_USER,
	POSTGRES_PASSWORD,
	POSTGRES_DB,
)

from env import *


def make_connection(db):
	match db:
		case "pg":
			conn = psycopg2.connect(
				host=POSTGRES_HOST,
				user=POSTGRES_USER,
				password=POSTGRES_PASSWORD,
				dbname=POSTGRES_DB,
				port=POSTGRES_PORT,
			)
			return conn, "pg"
		case "mysql":
			conn = mysql.connector.connect(
				host=MYSQL_HOST,
				user=MYSQL_USER,
				password=MYSQL_PASSWORD,
				database=MYSQL_DB,
				port=MYSQL_PORT,
			)
			return conn, "mysql"
		case "mongo6":
			client = pymongo.MongoClient(MONGO6_HOST, port=int(MONGO6_PORT), username=MONGO6_USER, password=MONGO6_PASSWORD)
			return  client[MONGO6_DB], "mongo6"
		case "mongo8":
			client = pymongo.MongoClient(MONGO8_HOST, port=int(MONGO8_PORT), username=MONGO8_USER, password=MONGO8_PASSWORD)
			return  client[MONGO8_DB], "mongo8"

def disconnect(conn, db):
	match db:
		case "pg":
			conn.close()
		case "mysql":
			conn.close()
		case "mongo6":
			conn.client.close()
		case "mongo8":
			conn.client.close()
def execute(db, conn):
	user_id = "86e1d601-7eca-4cb6-aa3c-e9593b3552e3"

	if db in ["pg", "mysql"]:
		cursor = conn.cursor()
		query = f"""
			SELECT COUNT(*) 
			FROM parameters_logs
			WHERE user_id = '{user_id}';
		"""
		cursor.execute(query)
		_ = cursor.fetchone()
		cursor.close()

	elif db in ["mongo6", "mongo8"]:
		collection = conn["users"]
		pipeline = [
			{ "$match": { "id": user_id } },
			{ "$unwind": "$parameters_logs" },
			{ "$count": "total" }
		]
		_ = list(collection.aggregate(pipeline))


def after(db, conn):
	return

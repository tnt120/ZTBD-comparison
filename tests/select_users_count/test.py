def execute(db, conn):
	if db in ["pg", "mysql"]:
		cursor = conn.cursor()
		query = """
			SELECT COUNT(*) 
			FROM users;
		"""
		cursor.execute(query)
		_ = cursor.fetchone()
		cursor.close()

	elif db in ["mongo6", "mongo8"]:
		collection = conn["users"]
		_ = collection.count_documents({})


def after(db, conn):
	return

def execute(db, conn):
    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        query = """
			SELECT 
				id,
				name,
				symbol
			FROM units;
		"""
        cursor.execute(query)
        _ = cursor.fetchall()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["units"]
        pipeline = [{"$project": {"_id": 1, "name": 1, "symbol": 1}}]
        _ = list(collection.aggregate(pipeline))


def after(db, conn):
    return

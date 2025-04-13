def execute(db, conn):
	if db in ["pg", "mysql"]:
		cursor = conn.cursor()
		query = """
			SELECT 
				id,
				name,
				hint,
				min_value,
				max_value,
				min_standard_value,
				max_standard_value
			FROM parameters
			WHERE name LIKE '%a%'
			ORDER BY name ASC;
		"""
		cursor.execute(query)
		_ = cursor.fetchall()
		cursor.close()

	elif db in ["mongo6", "mongo8"]:
		collection = conn["parameters"]
		filter_ = { "name": { "$regex": "a", "$options": "i" } }
		projection = {
			"id": 1,
			"name": 1,
			"hint": 1,
			"min_value": 1,
			"max_value": 1,
			"min_standard_value": 1,
			"max_standard_value": 1,
		}
		_ = list(collection.find(filter_, projection).sort("name", 1))


def after(db, conn):
	return

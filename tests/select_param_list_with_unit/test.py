def execute(db, conn):
	if db in ["pg", "mysql"]:
		cursor = conn.cursor()
		query = """
			SELECT 
				p.id,
				p.name,
				p.hint,
				p.min_value,
				p.max_value,
				p.min_standard_value,
				p.max_standard_value,
				u.name AS unit_name
			FROM parameters p
			JOIN units u ON p.unit_id = u.id
			ORDER BY p.name ASC;
		"""
		cursor.execute(query)
		_ = cursor.fetchall()
		cursor.close()

	elif db in ["mongo6", "mongo8"]:
		collection = conn["parameters"]
		pipeline = [
			{
				"$lookup": {
					"from": "units",
					"localField": "unit_id",
					"foreignField": "id",
					"as": "unit"
				}
			},
			{ "$unwind": "$unit" },
			{
				"$project": {
					"id": 1,
					"name": 1,
					"hint": 1,
					"min_value": 1,
					"max_value": 1,
					"min_standard_value": 1,
					"max_standard_value": 1,
					"unit_name": "$unit.name"
				}
			},
			{ "$sort": { "name": 1 } },
		]
		_ = list(collection.aggregate(pipeline))


def after(db, conn):
	return

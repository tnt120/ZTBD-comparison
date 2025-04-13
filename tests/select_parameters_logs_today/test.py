from datetime import date

def execute(db, conn):
	user_id = "32da9bf7-aacc-4a29-82ba-f9c1ddee4abc"
	today = str(date.today())

	if db in ["pg", "mysql"]:
		cursor = conn.cursor()
		query = f"""
			SELECT 
				p.name AS parameter_name,
				pl.value,
				pl.created_at
			FROM parameters_logs pl
			JOIN parameters p ON pl.parameter_id = p.id
			WHERE pl.user_id = '{user_id}'
			AND DATE(pl.created_at) = CURRENT_DATE;
		"""
		cursor.execute(query)
		_ = cursor.fetchall()
		cursor.close()

	elif db in ["mongo6", "mongo8"]:
		collection = conn["users"]
		pipeline = [
			{ "$match": { "id": user_id } },
			{ "$unwind": "$parameters_logs" },
			{ "$match": { "parameters_logs.created_at": today } },
			{
				"$lookup": {
					"from": "parameters",
					"localField": "parameters_logs.parameter_id",
					"foreignField": "id",
					"as": "parameter"
				}
			},
			{ "$unwind": "$parameter" },
			{
				"$project": {
					"parameter_name": "$parameter.name",
					"value": "$parameters_logs.value",
					"created_at": "$parameters_logs.created_at"
				}
			},
		]
		_ = list(collection.aggregate(pipeline))


def after(db, conn):
	return

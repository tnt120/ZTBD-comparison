from datetime import date

def execute(db, conn):
	user_id = "4fb046bf-6d6b-4a5d-aedb-787a3b0dac2b"
	today = str(date.today())

	if db in ["pg", "mysql"]:
		cursor = conn.cursor()
		query = f"""
			SELECT 
				d.name AS drug_name,
				d.power AS drug_power,
				dl.created_at,
				dl.taken_time,
				dl.time
			FROM drugs_logs dl
			JOIN drugs d ON dl.drug_id = d.id
			WHERE dl.user_id = '{user_id}'
			AND DATE(dl.created_at) = CURRENT_DATE;
		"""
		cursor.execute(query)
		_ = cursor.fetchall()
		cursor.close()

	elif db in ["mongo6", "mongo8"]:
		collection = conn["users"]
		pipeline = [
			{ "$match": { "id": user_id } },
			{ "$unwind": "$drugs_logs" },
			{ "$match": { "drugs_logs.created_at": today } },
			{
				"$lookup": {
					"from": "drugs",
					"localField": "drugs_logs.drug_id",
					"foreignField": "id",
					"as": "drug"
				}
			},
			{ "$unwind": "$drug" },
			{
				"$project": {
					"drug_name": "$drug.name",
					"drug_power": "$drug.power",
					"created_at": "$drugs_logs.created_at",
					"taken_time": "$drugs_logs.taken_time",
					"time": "$drugs_logs.time"
				}
			},
		]
		_ = list(collection.aggregate(pipeline))


def after(db, conn):
	return

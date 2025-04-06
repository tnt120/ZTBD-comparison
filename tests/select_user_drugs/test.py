def execute(db, conn):
	if db in ["pg", "mysql"]:
		cursor = conn.cursor()
		query = """
			SELECT 
				u.email,
				d.name AS drug_name,
				d.company,
				ud.dose_size,
				ud.amount,
				ud.start_date,
				ud.end_date
			FROM user_drugs ud
			JOIN users u ON ud.user_id = u.id
			JOIN drugs d ON ud.drug_id = d.id
			LIMIT 1000;
		"""
		cursor.execute(query)
		_ = cursor.fetchall()
		cursor.close()

	elif db in ["mongo6", "mongo8"]:
		collection = conn["users"]
		pipeline = [
			{
				"$project": {
					"email": 1,
					"user_drugs.dose_size": 1,
					"user_drugs.amount": 1,
					"user_drugs.start_date": 1,
					"user_drugs.end_date": 1,
					"user_drugs.drug_id": 1
				}
			},
			{ "$limit": 1000 }
		]
		_ = list(collection.aggregate(pipeline))

	
def after(db, conn):
	return
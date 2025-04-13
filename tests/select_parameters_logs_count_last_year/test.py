from datetime import date, timedelta

def execute(db, conn):
	user_id = "3c82d834-cf1f-411f-a490-0ed70031f979"
	today = date.today()
	one_year_ago = today - timedelta(days=365)

	if db in ["pg", "mysql"]:
		cursor = conn.cursor()
		query = f"""
			SELECT COUNT(*) 
			FROM parameters_logs
			WHERE user_id = '{user_id}'
			AND created_at BETWEEN '{one_year_ago}' AND '{today}';
		"""
		cursor.execute(query)
		_ = cursor.fetchone()
		cursor.close()

	elif db in ["mongo6", "mongo8"]:
		collection = conn["users"]
		pipeline = [
			{ "$match": { "id": user_id } },
			{ "$unwind": "$parameters_logs" },
			{ "$match": { "parameters_logs.created_at": { "$gte": str(one_year_ago) } } },
			{ "$count": "total" }
		]
		_ = list(collection.aggregate(pipeline))


def after(db, conn):
	return

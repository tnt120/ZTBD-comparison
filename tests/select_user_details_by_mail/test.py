def execute(db, conn):
	user_email = 'owoodward@cabrera.com'

	if db in ["pg", "mysql"]:
		cursor = conn.cursor()
		query = f"""
			SELECT 
				id,
				email,
				name,
				surname,
				birth_date,
				sex
			FROM users
			WHERE email = '{user_email}'
			LIMIT 1;
		"""
		cursor.execute(query)
		_ = cursor.fetchone()
		cursor.close()

	elif db in ["mongo6", "mongo8"]:
		collection = conn["users"]
		filter_ = { "email": user_email }
		projection = {
			"id": 1,
			"email": 1,
			"name": 1,
			"surname": 1,
			"birth_date": 1,
			"sex": 1
		}
		_ = collection.find_one(filter_, projection)


def after(db, conn):
	return

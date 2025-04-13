def execute(db, conn):
    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        query = """
			SELECT 
				u.id,
				email,
				name,
				surname,
				birth_date,
				creation_date,
				sex,
				COUNT(pl.id) AS tracked_parameters,
				COUNT(ud.id) AS tracked_drugs
			FROM users u
				LEFT JOIN parameters_logs pl ON pl.user_id = u.id
				LEFT JOIN user_drugs ud ON ud.user_id = u.id
			GROUP BY u.id, u.email, u.name, u.surname, u.birth_date, u.creation_date, u.sex;
		"""
        cursor.execute(query)
        _ = cursor.fetchall()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]

        pipeline = [
            {
                "$lookup": {
                    "from": "parameters_logs",
                    "localField": "id",
                    "foreignField": "user_id",
                    "as": "parameters_logs",
                }
            },
            {
                "$lookup": {
                    "from": "user_drugs",
                    "localField": "id",
                    "foreignField": "user_id",
                    "as": "user_drugs",
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "email": 1,
                    "name": 1,
                    "surname": 1,
                    "birth_date": 1,
                    "creation_date": 1,
                    "sex": 1,
                    "tracked_parameters": {"$size": "$parameters_logs"},
                    "tracked_drugs": {"$size": "$user_drugs"},
                }
            },
        ]
        _ = list(collection.aggregate(pipeline))


def after(db, conn):
    return

from datetime import datetime


def execute(db, conn):
    user_id = "9300cea6-6fbe-4beb-bc74-27d32d45d7e0"

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        query = f"""
			SELECT
				pl.id,
				created_at,
				value,
				p.name,
				p.hint,
				p.max_standard_value,
				p.min_standard_value,
				p.max_value,
				p.min_value,
				u.name as unit_name,
				u.symbol as unit_symbol
			FROM parameters_logs pl
				INNER JOIN parameters p on p.id = pl.parameter_id
				INNER JOIN units u on u.id = p.unit_id
			WHERE pl.user_id = '{user_id}'
			ORDER BY created_at DESC;
			"""
        cursor.execute(query)
        _ = cursor.fetchall()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]

        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$unwind": "$parameters_logs"},
            {
                "$lookup": {
                    "from": "parameters",
                    "localField": "parameters_logs.parameter_id",
                    "foreignField": "_id",
                    "as": "parameter_info",
                }
            },
            {"$unwind": "$parameter_info"},
            {
                "$lookup": {
                    "from": "units",
                    "localField": "parameter_info.unit_id",
                    "foreignField": "_id",
                    "as": "unit_info",
                }
            },
            {"$unwind": "$unit_info"},
            {
                "$project": {
                    "_id": 0,
                    "parameters_logs.id": 1,
                    "parameters_logs.created_at": 1,
                    "parameters_logs.value": 1,
                    "parameter_info.name": 1,
                    "parameter_info.hint": 1,
                    "parameter_info.max_standard_value": 1,
                    "parameter_info.min_standard_value": 1,
                    "parameter_info.max_value": 1,
                    "parameter_info.min_value": 1,
                    "unit_info.name": 1,
                    "unit_info.symbol": 1,
                }
            },
            {"$sort": {"parameters_logs.created_at": -1}},
        ]

        _ = list(collection.aggregate(pipeline))


def after(db, conn):
    return

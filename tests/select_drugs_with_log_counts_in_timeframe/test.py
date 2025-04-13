from datetime import datetime, timedelta


def execute(db, conn):
    drug_id = "100001901"

    if db in ["pg", "mysql"]:
        cursor = conn.cursor()
        query = f"""
		   SELECT
			d.id,
			d.company,
			d.name,
			d.info,
			SUM(CASE WHEN dl.created_at = CURRENT_DATE THEN 1 ELSE 0 END) AS log_count_today,
			SUM(CASE WHEN dl.created_at BETWEEN CURRENT_DATE - INTERVAL '4 DAY' AND CURRENT_DATE + INTERVAL '4 DAY' THEN 1 ELSE 0 END) AS log_count_4_days,
			COUNT(CASE WHEN dl.created_at IS NOT NULL THEN 1 END) AS log_count_all_time
		FROM drugs_logs dl
		INNER JOIN drugs d ON dl.drug_id = d.id
		GROUP BY d.id, d.company, d.name, d.info;
			"""

        if db == "mysql":
            query = query.replace(
                "CURRENT_DATE - INTERVAL '4 DAY'",
                "DATE_SUB(CURRENT_DATE, INTERVAL 4 DAY)",
            )
            query = query.replace(
                "CURRENT_DATE + INTERVAL '4 DAY'",
                "DATE_ADD(CURRENT_DATE, INTERVAL 4 DAY)",
            )

        cursor.execute(query)
        _ = cursor.fetchall()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["drugs"]

        today_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        four_days_ago = today_date - timedelta(days=4)
        four_days_from_now = today_date + timedelta(days=4)

        pipeline = [
            {"$match": {"id": drug_id}},
            {
                "$lookup": {
                    "from": "drug_logs",
                    "localField": "id",
                    "foreignField": "drug_id",
                    "as": "logs",
                }
            },
            {"$unwind": "$logs"},
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "company": 1,
                    "name": 1,
                    "info": 1,
                    "log_count_today": {
                        "$cond": [
                            {
                                "$eq": [
                                    {
                                        "$dateToString": {
                                            "format": "%Y-%m-%d",
                                            "date": "$logs.created_at",
                                        }
                                    },
                                    today_date.strftime("%Y-%m-%d"),
                                ]
                            },
                            1,
                            0,
                        ]
                    },
                    "log_count_4_days": {
                        "$cond": [
                            {
                                "$and": [
                                    {"$gte": ["$logs.created_at", four_days_ago]},
                                    {"$lte": ["$logs.created_at", four_days_from_now]},
                                ]
                            },
                            1,
                            0,
                        ]
                    },
                    "log_count_all_time": {
                        "$cond": [{"$ne": ["$logs.created_at", None]}, 1, 0]
                    },
                }
            },
            {
                "$group": {
                    "_id": "$id",
                    "company": {"$first": "$company"},
                    "name": {"$first": "$name"},
                    "info": {"$first": "$info"},
                    "log_count_today": {"$sum": "$log_count_today"},
                    "log_count_4_days": {"$sum": "$log_count_4_days"},
                    "log_count_all_time": {"$sum": "$log_count_all_time"},
                }
            },
        ]

        _ = list(collection.aggregate(pipeline))


def after(db, conn):
    return

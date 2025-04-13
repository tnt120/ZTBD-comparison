from datetime import datetime


def execute(db, conn):
    user_id = "9300cea6-6fbe-4beb-bc74-27d32d45d7e0"

    if db in ["pg", "mysql"]:
        today = datetime.today()

        cursor = conn.cursor()
        query = f"""
			SELECT
				drugs.id,
				atc_codes,
				characteristic,
				company,
				info,
				name,
				permit_expiration,
				permit_number,
				pharmaceutical_form_name,
				power,
				procedure_type,
				ddd.day
			FROM drugs
					INNER JOIN user_drugs ud on drugs.id = ud.drug_id
					INNER JOIN drug_dose_day ddd on ud.id = ddd.user_drug_id
			WHERE ud.user_id = '{user_id}'
			AND CURRENT_DATE BETWEEN start_date AND end_date
			AND ddd.day = UPPER('{today.strftime('%A')}')
			"""
        cursor.execute(query)
        _ = cursor.fetchall()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["users"]
        today_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        today_day = datetime.today().strftime("%A").upper()

        pipeline = [
            {
                "$match": {
                    "user_drugs.user_id": user_id,
                    "user_drugs.start_date": {"$lte": today_date},
                    "user_drugs.end_date": {"$gte": today_date},
                    "user_drugs.drug_dose_day": today_day,
                }
            },
            {"$unwind": "$user_drugs"},
            {"$match": {"user_drugs.drug_dose_day": today_day}},
            {
                "$project": {
                    "_id": 0,
                    "user_drugs.drug_id": 1,
                    "user_drugs.amount": 1,
                    "user_drugs.dose_size": 1,
                    "user_drugs.start_date": 1,
                    "user_drugs.end_date": 1,
                    "user_drugs.priority": 1,
                    "user_drugs.drug_dose_day": 1,
                    "user_drugs.drug_dose_time": 1,
                }
            },
            {
                "$lookup": {
                    "from": "drugs",
                    "localField": "user_drugs.drug_id",
                    "foreignField": "_id",
                    "as": "drug_info",
                }
            },
            {"$unwind": "$drug_info"},
            {
                "$project": {
                    "drug_info.id": 1,
                    "drug_info.atc_codes": 1,
                    "drug_info.characteristic": 1,
                    "drug_info.company": 1,
                    "drug_info.info": 1,
                    "drug_info.name": 1,
                    "drug_info.permit_expiration": 1,
                    "drug_info.permit_number": 1,
                    "drug_info.pharmaceutical_form_name": 1,
                    "drug_info.power": 1,
                    "drug_info.procedure_type": 1,
                    "user_drugs.day": 1,
                }
            },
        ]

        _ = list(collection.aggregate(pipeline))


def after(db, conn):
    return

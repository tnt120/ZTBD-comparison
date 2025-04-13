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
                d.power,
                dp.gtin_code,
                dp.pack_size,
                dp.pack_type,
                dp.pack_unit,
                dp.packages_quantity,
                dp.accessibility_category
            FROM drugs d
                INNER JOIN drug_packs dp on d.id = dp.drug_id
            WHERE d.id = '{drug_id}'
            """
        cursor.execute(query)
        _ = cursor.fetchall()
        cursor.close()

    elif db in ["mongo6", "mongo8"]:
        collection = conn["drugs"]

        pipeline = [
            {"$match": {"id": drug_id}},
            {
                "$lookup": {
                    "from": "drug_packs",
                    "localField": "id",
                    "foreignField": "drug_id",
                    "as": "drug_pack_info",
                }
            },
            {"$unwind": "$drug_pack_info"},
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "company": 1,
                    "name": 1,
                    "info": 1,
                    "power": 1,
                    "drug_pack_info.gtin_code": 1,
                    "drug_pack_info.pack_size": 1,
                    "drug_pack_info.pack_type": 1,
                    "drug_pack_info.pack_unit": 1,
                    "drug_pack_info.packages_quantity": 1,
                    "drug_pack_info.accessibility_category": 1,
                }
            },
        ]

        _ = list(collection.aggregate(pipeline))


def after(db, conn):
    return

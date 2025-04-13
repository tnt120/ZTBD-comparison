from psycopg2 import sql


def revert_update_postgres(connection, table_name, original_records, primary_key):
    columns = original_records[0].keys()

    try:
        with connection.cursor() as cursor:
            for record in original_records:
                set_clause = sql.SQL(", ").join(
                    sql.SQL("{} = {}").format(sql.Identifier(col), sql.Placeholder())
                    for col in columns
                    if col != primary_key
                )
                query = sql.SQL(
                    """
					UPDATE {table_name}
					SET {set_clause}
					WHERE {primary_key} = %s;
					"""
                ).format(
                    table_name=sql.Identifier(table_name),
                    set_clause=set_clause,
                    primary_key=sql.Identifier(primary_key),
                )
                values = tuple(record[col] for col in columns if col != primary_key) + (
                    record[primary_key],
                )
                cursor.execute(query, values)
            connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"Error while reverting update in PostgreSQL: {e}")


def revert_update_mysql(connection, table_name, original_records, primary_key):
    columns = original_records[0].keys()

    try:
        with connection.cursor() as cursor:
            for record in original_records:
                set_clause = ", ".join(
                    f"`{col}` = %s" for col in columns if col != primary_key
                )
                query = f"""
					UPDATE `{table_name}`
					SET {set_clause}
					WHERE `{primary_key}` = %s;
				"""
                values = tuple(record[col] for col in columns if col != primary_key) + (
                    record[primary_key],
                )
                cursor.execute(query, values)
            connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"Error while reverting update in MySQL: {e}")


def revert_update_mongo(
    conn, collection, original_records, subfield=None, subfield_id=None
):
    try:
        for record in original_records:
            if not subfield:
                query = {"_id": record["_id"]}
                update = {"$set": record}
                conn[collection].update_one(query, update)
            else:
                if not subfield_id:
                    raise ValueError("Missing subfield_id for nested array update.")

                parts = subfield.split(".")
                if len(parts) == 2:
                    parent_array, field_name = parts

                    query = {f"{parent_array}.id": subfield_id}
                    update = {"$set": {f"{parent_array}.$.{field_name}": record}}

                    conn[collection].update_one(query, update)
                elif len(parts) == 1:
                    query = {f"{subfield}.id": subfield_id}
                    update = {"$set": {f"{subfield}.$": record}}

                    conn[collection].update_one(query, update)

    except Exception as e:
        print(f"Error while reverting update in MongoDB: {e}")

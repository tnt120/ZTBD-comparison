from psycopg2 import sql


def revert_deletion_postgres(connection, table_name, existing_records):
    columns = existing_records[0].keys()  # Get column names from the first record
    values = [
        tuple(record.values()) for record in existing_records
    ]  # Convert records to tuples
    columns_sql = sql.SQL(", ").join(
        map(sql.Identifier, columns)
    )  # Format column names for SQL

    # Ensure the length of each value tuple matches the number of columns in the table
    try:
        with connection.cursor() as cursor:
            # Create a query with placeholders for each value
            query = sql.SQL(
                """
				INSERT INTO {table_name} ({columns})
				VALUES {values}
				ON CONFLICT (id) DO NOTHING;  -- Make sure 'id' or another unique column is in conflict
				"""
            ).format(
                table_name=sql.Identifier(table_name),
                columns=columns_sql,
                values=sql.SQL(", ").join(
                    [sql.SQL("(%s)")] * len(values[0])
                ),  # Ensure placeholders are tuples for each record
            )

            print(query)  # Print query for debugging

            # Use executemany to execute the query with the values
            cursor.executemany(
                query, values
            )  # Bind the correct values to the placeholders
            connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"Error while reverting deletion: {e}")


def revert_deletion_mysql(connection, table_name, existing_records):
    columns = existing_records[0].keys()
    values = [tuple(record.values()) for record in existing_records]
    columns_sql = ", ".join(f"`{col}`" for col in columns)
    placeholders = ", ".join(["%s"] * len(columns))

    try:
        with connection.cursor() as cursor:
            query = f"""
				INSERT IGNORE INTO `{table_name}` ({columns_sql})
				VALUES ({placeholders});
			"""
            cursor.executemany(query, values)
            connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"Error while reverting deletion in MySQL: {e}")


def revert_deletion_mongo(
    conn, collection, existing_records, subfield=None, target_id=None
):
    try:
        if subfield:
            for record in existing_records:
                conn[collection].update_one(
                    {"_id": target_id},
                    {"$push": {subfield: record}},
                    upsert=True,
                )
        else:
            for record in existing_records:
                conn[collection].insert_one(record)
    except Exception as e:
        print(f"Error while reverting deletion in MongoDB: {e}")

def revert_insert_postgres(connection, table_name, ids):
    if not ids:
        return
    query = f"DELETE FROM {table_name} WHERE id = ANY(ARRAY[%s]::uuid[])"
    with connection.cursor() as cursor:
        cursor.execute(query, (ids,))
    connection.commit()


def revert_insert_mysql(connection, table_name, ids):
    if not ids:
        return
    query = f"DELETE FROM {table_name} WHERE id IN ({', '.join(['%s'] * len(ids))})"
    with connection.cursor() as cursor:
        cursor.execute(query, ids)
    connection.commit()


def revert_insert_mongo(connection, collection, ids, subfield=None):
    if not ids:
        return

    if subfield:
        query = {f"{subfield}._id": {"$in": ids}}
        update = {"$pull": {subfield: {"_id": {"$in": ids}}}}
        connection[collection].update_many(query, update)
    else:
        connection[collection].delete_many({"_id": {"$in": ids}})

def import_postgres_parameters(records_count, records=None):
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        dbname=POSTGRES_DB,
        port=POSTGRES_PORT,
    )
    cursor = conn.cursor()

    if records is None:
        records = import_n_records(INPUT_FILE, records_count)

    if records == False:
        print_colored("[PostgreSQL] Can't continue", "RED")
        return

    print_colored(
        f'[PostgreSQL] Inserting {get_colored(len(records), "WHITE", restore={"color":"BLUE"})} records',
        "BLUE",
    )

    start = time()
    batch = []
    for rec in tqdm(records, desc="Inserting"):
        batch.append(
            (
                rec["id"],
                datetime.fromisoformat(rec["created_at"]),
                rec["value"],
                rec["parameter_id"],
                rec["user_id"],
            )
        )
        if len(batch) >= 10000:
            args_str = ",".join(
                cursor.mogrify("(%s,%s,%s,%s,%s)", b).decode("utf-8") for b in batch
            )
            cursor.execute(
                "INSERT INTO parameters_logs (id, created_at, value, parameter_id, user_id) VALUES "
                + args_str
            )
            conn.commit()
            batch = []
    if batch:
        args_str = ",".join(
            cursor.mogrify("(%s,%s,%s,%s,%s)", b).decode("utf-8") for b in batch
        )
        cursor.execute(
            "INSERT INTO parameters_logs (id, created_at, value, parameter_id, user_id) VALUES "
            + args_str
        )
        conn.commit()
    end = time()
    cursor.close()
    conn.close()

    return end - start

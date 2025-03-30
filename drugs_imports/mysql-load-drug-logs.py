import mysql.connector
import re

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="mysql_ZTBD",
    port="3307"
)
cursor = conn.cursor()

with open("drug_packs.sql", "r", encoding="utf-8") as file:

    pattern = re.compile(r"INSERT INTO public\.drug_packs \(\s*id,\s*(.*?)\) VALUES \((\d+),\s*(.*?)\);", re.DOTALL)

    def remove_id_column(match):
        columns = match.group(1)
        values = match.group(3)
        return f"INSERT INTO public.drug_packs ({columns}) VALUES ({values});"


    modified_sql = pattern.sub(remove_id_column, file.read())

    for line in modified_sql.split(";"):
        line = line.strip()
        if not line or not line.lower().startswith("insert"):
            continue

        line = re.sub(r'INSERT INTO\s+public\.', 'INSERT INTO ', line, flags=re.IGNORECASE)
        print(line)
        cursor.execute(line)

conn.commit()
cursor.close()

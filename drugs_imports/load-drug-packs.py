import psycopg2
import re

conn = psycopg2.connect(
    dbname="postgres_ZTBD",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5433"
)
cursor = conn.cursor()

with open("drug_packs.sql", "r", encoding="utf-8") as file:
    sql = file.read()

pattern = re.compile(r"INSERT INTO public\.drug_packs \(\s*id,\s*(.*?)\) VALUES \((\d+),\s*(.*?)\);", re.DOTALL)

def remove_id_column(match):
    columns = match.group(1)
    values = match.group(3)
    return f"INSERT INTO public.drug_packs ({columns}) VALUES ({values});"


modified_sql = pattern.sub(remove_id_column, sql)

cursor.execute(modified_sql)

conn.commit()
cursor.close()
conn.close()

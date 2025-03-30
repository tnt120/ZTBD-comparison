import psycopg2

conn = psycopg2.connect(
    dbname="postgres_ZTBD",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5433"
)
cursor = conn.cursor()

with open("drugs.sql", "r", encoding="utf-8") as file:
    sql = file.read()

cursor.execute(sql)

conn.commit()
cursor.close()
conn.close()

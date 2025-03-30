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

with open("drugs.sql", "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if not line or not line.lower().startswith("insert"):
            continue

        line = re.sub(r'INSERT INTO\s+public\.', 'INSERT INTO ', line, flags=re.IGNORECASE)
        print(line)
        cursor.execute(line)

conn.commit()
cursor.close()

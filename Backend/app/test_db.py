from database import get_connection

conn = get_connection()

with conn.cursor() as cur:
    cur.execute("SELECT version();")
    version = cur.fetchone()

print(version[0])

conn.close()
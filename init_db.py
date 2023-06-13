import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="VK",
        user=os.environ['postgres'],
        password=os.environ['Qwerty123'])

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute('DROP TABLE IF EXISTS books;')


conn.commit()

cur.close()
conn.close()

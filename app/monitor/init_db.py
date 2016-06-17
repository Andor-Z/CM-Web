import sqlite3

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

cursor.execute('CREATE TABLE merory (time INTEGER primary key, memory INTEGER)')

cursor.close()
conn.commit()
conn.close()
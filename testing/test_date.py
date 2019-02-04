import datetime
import sqlite3

conn = sqlite3.connect("local_db.dt_type")

c = conn.cursor()

c.execute("SELECT date from lessons;")

r = c.fetchall()

dt = datetime.datetime.strptime(r[0][0], "%d-%m-%Y %I:%M%p")
# print(dt)

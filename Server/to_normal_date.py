from sql_handler import DataBaseWorker as dbw
import datetime

db = dbw()
c=db.connection.cursor()

c.execute("SELECT id, date FROM lessons;")

start = datetime.datetime(2018, 2, 5, 0, 0)

less = [
    datetime.timedelta(0, 9 * 3600 + 0 * 60),
    datetime.timedelta(0, 10 * 3600 + 45 * 60),
    datetime.timedelta(0, 13 * 3600 + 0 * 60),
    datetime.timedelta(0, 14 * 3600 + 45 * 60),
    datetime.timedelta(0, 16 * 3600 + 20 * 60),
    datetime.timedelta(0, 18 * 3600 + 15 * 60),
]

for line in c.fetchall():
    s={}
    date = int(line[1])
    delta = datetime.timedelta(date//100 * 7 + date%100//10)
    lesson = less[date%10]
    normal_date = (start + delta + lesson).strftime("%d-%m-%Y %I:%M%p")
    print(str(normal_date))
    print("Update lessons set date=date('" + str(normal_date) + "', 'yyyy-mm-dd hh:mi:ss') where id=" + str(line[0]))
    c.execute(
        "Update lessons set date='" + str(normal_date) + "' where id=" + str(line[0]))


# c.execute("SELECT id, date FROM lessons;")

print(c.fetchall())
db.connection.commit()

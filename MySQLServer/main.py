import MySQLdb
db1 = MySQLdb.connect(host="localhost",user="root",passwd="****")
cursor = db1.cursor()
sql = 'CREATE DATABASE chom'
cursor.execute(sql)
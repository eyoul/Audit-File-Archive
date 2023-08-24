import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="&CorSrvPa&111"
)
my_cursor = mydb.cursor()

my_cursor.execute("CREATE DATABASE lib")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)
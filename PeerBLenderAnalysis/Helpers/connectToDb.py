import mysql.connector
import sqlalchemy

from mysql.connector import errorcode

try:
    cnx = mysql.connector.connect(user='root', password='Darthpic0',
                                  host='localhost',
                                  database='diplomkatest')
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)

cursor = cnx.cursor(buffered=True)

cursor.execute("SELECT * from USER")
result = cursor.fetchall()
print (result)

cnx.close()
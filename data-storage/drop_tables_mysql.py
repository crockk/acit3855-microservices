import mysql.connector
db_conn = mysql.connector.connect(host="kafka-nolan.westus2.cloudapp.azure.com", user="showstarters",
password="password", database="showstarters")
db_cursor = db_conn.cursor()
db_cursor.execute('''
 DROP TABLE `show`, `ticket`
''')
db_conn.commit()
db_conn.close()
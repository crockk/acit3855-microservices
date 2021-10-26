import sqlite3

conn = sqlite3.connect('showstarters.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE show
          ''')

c.execute('''
          DROP TABLE ticket
          ''')

conn.commit()
conn.close()

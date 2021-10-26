import sqlite3

conn = sqlite3.connect('showstarters.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE IF NOT EXISTS show
          (id INTEGER PRIMARY KEY ASC,
           show_id INTEGER NOT NULL, 
           artist VARCHAR(250) NOT NULL,
           showtime DATETIME NOT NULL,
           venue VARCHAR(250) NOT NULL,
           available_tickets INTEGER NOT NULL,
           booking_contact VARCHAR(250) NULL,
           date_created DATETIME NULL)
          ''')

c.execute('''
          CREATE TABLE IF NOT EXISTS ticket
          (id INTEGER PRIMARY KEY ASC,
           ticket_id INTEGER NOT NULL, 
           ticket_holder VARCHAR(250) NOT NULL,
           purchase_date DATETIME NULL,
           contact VARCHAR(250) NULL,
           date_created DATETIME NULL,
           show INTEGER NOT NULL)
          ''')

conn.commit()
conn.close()

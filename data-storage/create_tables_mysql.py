import mysql.connector
db_conn = mysql.connector.connect(host="kafka-nolan.westus2.cloudapp.azure.com", user="showstarters",
password="password", database="showstarters")
db_cursor = db_conn.cursor()

db_cursor.execute('''
          CREATE TABLE IF NOT EXISTS `show` (
           `id` INT NOT NULL AUTO_INCREMENT,
           `show_id` INT NOT NULL, 
           `artist` VARCHAR(250) NOT NULL,
           `showtime` DATETIME NOT NULL,
           `venue` VARCHAR(250) NOT NULL,
           `available_tickets` INT NOT NULL,
           `booking_contact` VARCHAR(250) NULL,
           `date_created` DATETIME NULL,
           CONSTRAINT show_pk PRIMARY KEY (id)
        );
          ''')


db_cursor.execute('''
          CREATE TABLE IF NOT EXISTS `ticket` (
           `id` INT NOT NULL AUTO_INCREMENT,
           `ticket_id` INT NOT NULL, 
           `ticket_holder` VARCHAR(250) NOT NULL,
           `purchase_date` DATETIME NULL,
           `contact` VARCHAR(250) NULL,
           `date_created` DATETIME NULL,
           `show` INT NOT NULL,
           CONSTRAINT ticket_pk PRIMARY KEY (id)
        );
          ''')
db_conn.commit()
db_conn.close()
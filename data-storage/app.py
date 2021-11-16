#   app.py
#   Serves connexion Flaskapp for ShowStarters data storage API service.
#
#   Author: Nolan Crooks
#   BCIT A01190324
#
#   ACIT 3855 - Service Based Architectures
#

import json
import logging
import logging.config
from datetime import datetime
from threading import Thread

import connexion
import cryptography
import yaml
from connexion import NoContent
from pykafka import KafkaClient
from pykafka.common import OffsetType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from time import sleep

from base import Base
from show import Show
from ticket import Ticket

import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
   app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
   log_config = yaml.safe_load(f.read())
   logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s"% app_conf_file)
logger.info("Log Conf File: %s"% log_conf_file)

DB_USER = app_config['datastore']['user']
DB_PASS = app_config['datastore']['password']
DB_HOSTNAME = app_config['datastore']['hostname']
DB_PORT = app_config['datastore']['port']
DB_DATABASE = app_config['datastore']['db']

DB_ENGINE = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOSTNAME}:{DB_PORT}/{DB_DATABASE}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info(f"Connecting to DB. Hostname: {DB_HOSTNAME}, Port: {DB_PORT}")

def create_show_booking(body):
    """ Receives a show booking """

    session = DB_SESSION()

    booking = Show(int(body['show_id']),
                    body['artist'],
                    datetime.strptime(body['showtime'], '%Y-%m-%dT%H:%M:%SZ'),
                    body['venue'],
                    int(body['available_tickets']),
                    body['booking_contact'])


    session.add(booking)

    session.commit()

    session.close()

    id = body['show_id']
    logger.debug(f'Stored event create_show_booking request with a unique id of {id}')

    return NoContent, 201


def create_ticket_purchase(body):
    """ Receives ticket purchase """

    session = DB_SESSION()

    purchase = Ticket(int(body['ticket_id']),
                        body['ticket_holder'],
                        datetime.strptime(body['purchase_date'], '%Y-%m-%dT%H:%M:%S.%fZ'),
                        body['contact'],
                        int(body['show']))


    session.add(purchase)

    session.commit()

    session.close()

    id = body['ticket_id']
    logger.debug(f'Stored event create_ticket_purchase request with a unique id of {id}')


    return NoContent, 201


def get_shows(start_timestamp, end_timestamp):
    """ Gets new scheduled shows after the timestamp """
    session = DB_SESSION()

    start_timestamp_dt = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_dt = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    readings = session.query(Show).filter(Show.date_created >= start_timestamp_dt, Show.date_created < end_timestamp_dt)

    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Scheduled Shows after %s returns %d results" % (start_timestamp, len(results_list)))
    return results_list, 200

def get_tickets(start_timestamp, end_timestamp):
    """ Gets purchased tickets after the timestamp """
    session = DB_SESSION()
    
    start_timestamp_dt = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_dt = datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    readings = session.query(Ticket).filter(Ticket.date_created >= start_timestamp_dt, Ticket.date_created < end_timestamp_dt)

    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for tickets purchased after %s returns %d results" % (start_timestamp, len(results_list)))
    return results_list, 200

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                app_config["events"]["port"])

    connected = False
    max_retries = app_config['events']['retries']
    retries = 0
    while retries < max_retries and not connected:
        try:
            logger.info(f"Attempting to connect to Kafka. Retries remaining: {max_retries - retries}")
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            connected = True
        except Exception as e:
            retries += 1
            logger.error(f"Failed to connect to Kafka. Retries remaining: {max_retries - retries}")
            sleep(app_config['events']['wait'])

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                        reset_offset_on_start=False,
                                        auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "ticket": # Change this to your event type
            # Store the event1 (i.e., the payload) to the DB
            create_ticket_purchase(payload)
        elif msg["type"] == "show": # Change this to your event type
            # Store the event2 (i.e., the payload) to the DB
            create_show_booking(payload)
        # Commit the new message as being read
        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090, debug=False)


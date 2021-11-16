#   app.py
#   Serves connexion Flaskapp for ShowStarters API service.
#
#   Author: Nolan Crooks
#   BCIT A01190324
#
#   ACIT 3855 - Service Based Architectures
#

import datetime
import json
import logging
import logging.config

import connexion
import requests
import yaml
from connexion import NoContent
from pykafka import KafkaClient

from flask_cors import CORS, cross_origin
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

def get_ticket_purchase(index):
    """ Gets a ticket purchase event from event store"""

    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                        consumer_timeout_ms=1000)

    logger.info(f'Retrieving event ticket purchase at index = {index}')

    try:
        i = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] != 'ticket':
                continue

            logger.debug(f"msg = {msg}, i = {i}")
            event = msg['payload']
            if i == int(index):
                return event, 200
            i += 1
    except:
        logger.error("No more messages found")
    
    logger.error(f"Could not find show at index = {index}")
    return { "message": "Not Found"}, 404


def get_show(index):
    """ Gets a show event from event store"""

    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                        consumer_timeout_ms=1000)

    logger.info(f'Retrieving event show at index = {index}')

    try:
        i = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] != 'show':
                continue
            
            logger.debug(f"msg = {msg}, i = {i}")
            event = msg['payload']
            if i == int(index):
                return event, 200
            i += 1
    except:
        logger.error("No more messages found")
    
    logger.error(f"Could not find show at index = {index}")
    return { "message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'


if __name__ == '__main__':
    app.run(port=8010, debug=False)

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
from time import sleep

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

def purchase_ticket(body):
    """ Receives a ticket purchase event """

    id = body['ticket_id']
    logger.info(f'Received event purchase_ticket request with a unique id of {id}')

    # resp = requests.post(app_config['purchase_ticket']['url'] , json=body, headers={'Content-Type':'application/json'})
    # client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    # topic = client.topics[str.encode(app_config['events']['topic'])]
    # producer = topic.get_sync_producer()

    msg = { "type": "ticket",
            "datetime":
                datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "payload": body
        }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f'Received event purchase_ticket response with a unique id of {id}')

    return NoContent, 201


def book_show(body):
    """ Receives a book show event """

    id = body['show_id']
    logger.info(f'Received event schedule_show request with a unique id of {id}')

    # resp = requests.post(app_config['schedule_show']['url'], json=body, headers={'Content-Type':'application/json'})
    # client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    # topic = client.topics[str.encode(app_config['events']['topic'])]
    # producer = topic.get_sync_producer()

    msg = { "type": "show",
            "datetime":
                datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "payload": body
        }

    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f'Received event schedule_show response with a unique id of {id}')

    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/receiver", strict_validation=True, validate_responses=True)

connected = False
max_retries = app_config['events']['retries']
retries = 0
while retries < max_retries and not connected:
    try:
        logger.info(f"Attempting to connect to Kafka. Retries remaining: {max_retries - retries}")
        client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
        topic = client.topics[str.encode(app_config['events']['topic'])]
        producer = topic.get_sync_producer()
        connected = True
    except Exception as e:
        retries += 1
        logger.error(f"Failed to connect to Kafka. Retries remaining: {max_retries - retries}")
        sleep(app_config['events']['wait'])

if __name__ == '__main__':
    app.run(port=8080, debug=False)

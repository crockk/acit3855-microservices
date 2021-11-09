#   app.py
#   Serves connexion Flaskapp for ShowStarters API service.
#
#   Author: Nolan Crooks
#   BCIT A01190324
#
#   ACIT 3855 - Service Based Architectures
#

from threading import current_thread
import yaml
import logging
import logging.config
import requests
import connexion
import json
from connexion import NoContent
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from flask_cors import CORS, cross_origin

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def get_stats():
    """ Receives a get stats event """
    logger.info(f'Started processing get stats request')
    
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            stats = json.loads(f.read())
    except FileNotFoundError as e:
        logger.error(f"{e}")
        return 'Statistics do not exist', 404

    logger.debug(f"Stats content: {stats}")
    logger.info("Request has been completed.")

    return stats, 200


def populate_stats():
    """ Periodically update statistics """
    logger.info(f'Start periodic processing')
    
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            stats = json.loads(f.read())
    except FileNotFoundError as e:
        stats = {
            'num_tickets_purchased': 0,
            'num_shows_scheduled': 0,
            'num_shows_sold_out': 0,
            'busiest_venue': '',
            'last_updated': '2000-07-13T12:00:00.000Z'
        }
        
    current_timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    tickets_resp = requests.get(app_config['eventstore']['url'] + '/ticket' + f"?start_timestamp={stats['last_updated']}&end_timestamp={current_timestamp}")
    shows_resp = requests.get(app_config['eventstore']['url'] + '/show' + f"?start_timestamp={stats['last_updated']}&end_timestamp={current_timestamp}")

    for resp in (tickets_resp, shows_resp):
        if resp.status_code != 200:
            logger.error(f"Status code {resp.status_code} received from service: {resp.url}")
            return

    tickets = tickets_resp.json()
    shows = shows_resp.json()

    num_shows_sold_out = get_sold_out_shows(shows)
    busiest_venue = get_busiest_venue(shows)

    logger.info(f"Events recieved: {len(tickets) + len(shows)}")

    stats['num_tickets_purchased'] += len(tickets)
    stats['num_shows_scheduled'] += len(shows)
    stats['num_shows_sold_out'] += num_shows_sold_out
    stats['busiest_venue'] = busiest_venue
    stats['last_updated'] = current_timestamp

    with open(app_config['datastore']['filename'], 'w') as f:
        json.dump(stats, f)

    logger.debug(f'Wrote new stats to file: {stats}')

def get_sold_out_shows(shows):
    num_sold_out = 0
    for show in shows:
        if show['available_tickets'] == 0:
            num_sold_out += 1
    return num_sold_out

def get_busiest_venue(shows):
    venues = {}
    busiest = ''
    for show in shows:
        current_venue = show['venue']
        if current_venue in venues:
            venues[current_venue] += 1
        else:
            venues[current_venue] = 1
    if venues != {}:
        busiest = max(venues, key=venues.get)
    return busiest

def init_scheduler():
    """ Background process scheduler """
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
        'interval',
        seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'


if __name__ == '__main__':
    init_scheduler()
    app.run(port=8100, use_reloader=False, debug=False)

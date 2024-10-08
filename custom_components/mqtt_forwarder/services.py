import logging
import os
import datetime
import pytz
import requests

from paho.mqtt import client as mqtt_client

_LOGGER = logging.getLogger(__name__)


def send_mqtt(value: float, device_name: str, measurement: str, multiplier: float, site_id: int):
    mqtt_host = os.getenv('BAMBOO_MQTT_HOST')
    mqtt_user = os.getenv('BAMBOO_MQTT_USER')
    mqtt_pass = os.getenv('BAMBOO_MQTT_PASS')
    mqtt_port = os.getenv('BAMBOO_MQTT_PORT')

    if not mqtt_port:
        mqtt_port = 1883

    missing_variable = False

    if mqtt_host is None:
        _LOGGER.warning("Unable to find required environment variable BAMBOO_MQTT_HOST")
        missing_variable = True
    if mqtt_user is None:
        _LOGGER.warning("Unable to find required environment variable BAMBOO_MQTT_USER")
        missing_variable = True
    if mqtt_pass is None:
        _LOGGER.warning("Unable to find environment variable BAMBOO_MQTT_PASS. Please set this to authenticate MQTT messages")

    if missing_variable:
        return

    _LOGGER.info(f'''Calling send_mqtt with variables
mqtt_host = {mqtt_host}
site_id = {site_id}
mqtt_user = {mqtt_user}
mqtt_pass = {mqtt_pass}
value = {value}
device_name = {device_name}
measurement = {measurement}
multiplier = {multiplier}
port = {mqtt_port}
''')

    topic = f"/sites/{site_id}/measurements/{mqtt_user}"

    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d-%H-%M')

    # TODO: Change this so it's an object that get's jsonified
    payload = f'''[
  {{
    "device_name": "{device_name}",
    "measurements": [
      {{
        "time": "{timestamp}",
        "{measurement}": {value * multiplier}
      }}
    ]
  }}
]'''

    # TODO: Setup so there is one MQTT client that is reused
    client = mqtt_client.Client()
    if mqtt_pass:
        client.username_pw_set(mqtt_user, mqtt_pass)
    client.connect(mqtt_host, mqtt_port)
    client.loop_start()
    client.publish(topic, str(payload))
    client.disconnect()


def send_http(value: float, device_name: str, measurement: str, multiplier: float, site_id: int):
    http_host = os.getenv('BAMBOO_HTTP_HOST')
    http_user = os.getenv('BAMBOO_HTTP_USER')
    http_pass = os.getenv('BAMBOO_HTTP_PASS')

    missing_variable = False

    if http_host is None:
        _LOGGER.warning("Unable to find required environment variable BAMBOO_HTTP_HOST")
        missing_variable = True
    if http_user is None:
        _LOGGER.warning("Unable to find required environment variable BAMBOO_HTTP_USER")
        missing_variable = True
    if http_pass is None:
        _LOGGER.warning("Unable to find environment variable BAMBOO_HTTP_PASS. Please set this to authenticate HTTP messages")

    if missing_variable:
        return

    _LOGGER.debug(f'''Calling send_http with variables
http_host = {http_host}
site_id = {site_id}
http_user = {http_user}
http_pass = {http_pass}
value = {value}
device_name = {device_name}
measurement = {measurement}
multiplier = {multiplier}
''')

    token_url = http_host + "/token"
    login_data = f"username={http_user}&password={http_pass}"

    token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(token_url, data=login_data, headers=token_headers)
    _LOGGER.debug(token_url)
    _LOGGER.debug(response.status_code)

    token = ""

    if response.status_code == 200:
        token = response.json()['access_token']
    else:
        _LOGGER.info('Bamboo login request failed. URL:' + token_url)
        return

    endpoint = f"/sites/{site_id}/measurements"
    url = http_host + endpoint

    now = datetime.datetime.now(pytz.timezone('UTC'))
    timestamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    # TODO: Change this so it's an object that gets jsonified
    payload = f'''[
  {{
    "device_name": "{device_name}",
    "measurements": [
      {{
        "time": "{timestamp}",
        "{measurement}": {value * multiplier}
      }}
    ]
  }}
]'''

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, data=payload, headers=headers)

    _LOGGER.info(url)
    _LOGGER.info(response.status_code)

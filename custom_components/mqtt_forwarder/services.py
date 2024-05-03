import logging
import os
import datetime 

from paho.mqtt import client as mqtt_client

_LOGGER = logging.getLogger(__name__)


def send_mqtt(value: float, device_name: str, measurement: str, multiplier: float):
    mqtt_host = os.getenv('BAMBOO_MQTT_HOST')
    site_id = os.getenv('BAMBOO_SITE_ID')
    mqtt_user = os.getenv('BAMBOO_MQTT_USER')
    mqtt_pass = os.getenv('BAMBOO_MQTT_PASS')
    mqtt_port = os.getenv('BAMBOO_MQTT_PORT')

    if not mqtt_port:
        mqtt_port = 1883

    missing_variable = False

    if mqtt_host is None:
        _LOGGER.warn("Unable to find required environment variable BAMBOO_MQTT_HOST")
        missing_variable = True
    if site_id is None:
        _LOGGER.warn("Unable to find required environment variable BAMBOO_SITE_ID")
        missing_variable = True
    if mqtt_user is None:
        _LOGGER.warn("Unable to find required environment variable BAMBOO_MQTT_USER")
        missing_variable = True
    if mqtt_pass is None:
        _LOGGER.warn("Unable to find required environment variable BAMBOO_MQTT_PASS")
        missing_variable = True

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
port {mqtt_port}
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
    # if mqtt_user and mqtt_pass:
    # client.username_pw_set(mqtt_user, mqtt_pass)
    client.connect(mqtt_host, mqtt_port)
    client.loop_start()
    client.publish(topic, str(payload))
    client.disconnect()

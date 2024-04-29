import logging

from paho.mqtt import client as mqtt_client

_LOGGER = logging.getLogger(__name__)


def send_mqtt(host: str, port: int, topic: str, payload: str):
    # Setup so there is one MQTT client that is reused
    client = mqtt_client.Client()
    # client.username_pw_set(user, password)
    client.connect(host, port)
    client.loop_start()
    client.publish(topic, str(payload))
    client.disconnect()

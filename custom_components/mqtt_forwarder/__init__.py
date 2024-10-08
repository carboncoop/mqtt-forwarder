import logging
import os
from random import randrange

from homeassistant import core
from homeassistant.config_entries import ConfigEntry

from . import const
from . import services

_LOGGER = logging.getLogger(__name__)

entities = []


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:

    def handle_data_forward(call):
        # TODO: Add switch to select between mqtt and http
        services.send_http(call.data.get("value"), call.data.get("device_name"), call.data.get("measurement"), call.data.get("multiplier"), call.data.get("site_id"))

    hass.services.async_register(const.DOMAIN, "mqtt_forward", handle_data_forward)

    return True


async def async_setup_entry(hass: core.HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a mqtt forwarding entry from a config entry."""
    _LOGGER.info("Creating mqtt forwarding automation for entity " + entry.data["selected_entity"])

    random_id = randrange(1000000000000, 10000000000000)

    mqtt_message = f'''- id: '{random_id}'
  alias: MQTT forward - {entry.data["selected_entity"]}
  trigger:
    - entity_id: {entry.data["selected_entity"]}
      platform: state
  condition: []
  action:
    - service: mqtt_forwarder.mqtt_forward
      data_template:
        value: '{{{{trigger.to_state.state}}}}'
        device_name: {entry.data["device_name"]}
        measurement: {entry.data["measurement"]}
        multiplier: {entry.data["multiplier"]}
        site_id: {entry.data["site_id"]}
'''

    filename = os.path.join(const.AUTOMATION_LOCATION, entry.data["selected_entity"] + ".yaml")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    f = open(filename, "w")
    f.write(mqtt_message)
    f.close()

    await hass.services.async_call('automation', 'reload')

    return True


async def async_remove_entry(hass: core.HomeAssistant, entry: ConfigEntry) -> None:
    _LOGGER.info("Removing mqtt forwarding automation for entity " + entry.data["selected_entity"])
    filename = os.path.join(const.AUTOMATION_LOCATION, entry.data["selected_entity"] + ".yaml")

    os.remove(filename)

    await hass.services.async_call('automation', 'reload')

    return True

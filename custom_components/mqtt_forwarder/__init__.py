import logging
import os

from homeassistant import core
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_registry as er

from . import const

_LOGGER = logging.getLogger(__name__)

entities = []


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: core.HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a mqtt forwarding entry from a config entry."""
    _LOGGER.info("Creating mqtt forwarding automation for entity " + entry.data["selected_device"])

    mqtt_message = f'''- id: '1558647997872'
  alias: MQTT forward - {entry.data["selected_device"]}
  trigger:
    - entity_id: {entry.data["selected_device"]}
      platform: state
  condition: []
  action:
    - service: mqtt.publish
      data_template:
        payload: '{{ "entity": "{{{{trigger.entity_id}}}}", "value": {{{{trigger.to_state.state}}}}}}'
        topic: homeassistant/incomming
'''

    filename = os.path.join(const.AUTOMATION_LOCATION, entry.data["selected_device"] + ".yaml")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    f = open(filename, "w")
    f.write(mqtt_message)
    f.close()

    _LOGGER.debug("Calling automation reload")
    await hass.services.async_call('automation', 'reload')
    _LOGGER.debug("Finished automation reload")

    return True


async def async_remove_entry(hass: core.HomeAssistant, entry: ConfigEntry) -> None:
    _LOGGER.info("Removing mqtt forwarding automation for entity " + entry.data["selected_device"])
    filename = os.path.join(const.AUTOMATION_LOCATION, entry.data["selected_device"] + ".yaml")

    os.remove(filename)

    await hass.services.async_call('automation', 'reload')

    return True

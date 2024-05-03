import logging

from typing import Any, Dict, Optional

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv

import voluptuous as vol

from . import const

_LOGGER = logging.getLogger(__name__)

MEASUREMENT_LIST = ["power",
                    "consumption",
                    ]


class ConfigFlowHandler(config_entries.ConfigFlow, domain=const.DOMAIN):
    """Handle a config or options flow for mqtt forwarder."""

    _mqtt_host = ""

    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        entities_schema_local = vol.Schema({vol.Required("selected_entity"): vol.In(list(self.hass.states.async_entity_ids())),
                                            vol.Required("device_name"): cv.string,
                                            vol.Required("measurement"): vol.In(MEASUREMENT_LIST),
                                            vol.Required("multiplier", default=1.0): vol.Coerce(float)})

        errors: Optional[Dict[str, Any]] = {}

        if user_input is not None:
            if not errors:
                self.data = user_input

                return self.async_create_entry(title="MQTT forwarding " + user_input["selected_entity"], data=self.data)

        return self.async_show_form(
            step_id="user", data_schema=entities_schema_local, errors=errors
        )

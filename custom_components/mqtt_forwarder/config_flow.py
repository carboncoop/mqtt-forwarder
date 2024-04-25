import logging

from typing import Any, Dict, Optional

from homeassistant import config_entries

import voluptuous as vol

from . import const

_LOGGER = logging.getLogger(__name__)


class ConfigFlowHandler(config_entries.ConfigFlow, domain=const.DOMAIN):
    """Handle a config or options flow for mqtt forwarder."""

    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        entities_schema_local = vol.Schema({vol.Required("selected_device"): vol.In(list(self.hass.states.async_entity_ids()))})

        errors: Optional[Dict[str, Any]] = {}

        if user_input is not None:
            if not errors:
                # Input is valid, set data.
                self.data = user_input
                # Return the form of the next step.
                return self.async_create_entry(title="MQTT forwarding " + user_input["selected_device"], data=self.data)

        return self.async_show_form(
            step_id="user", data_schema=entities_schema_local, errors=errors
        )

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_API_TOKEN, CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from ecologi import Ecologi, NotFoundException

import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
    }
)


class EcologiConfigFlow(ConfigFlow, domain=DOMAIN):
    """The configuration flow for an Ecologi system."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}
        if user_input:
            try:
                impact = await self.hass.async_add_executor_job(
                    lambda: Ecologi().impact(
                        username=user_input[CONF_USERNAME],
                    )
                )
                if impact:
                    # Make sure we're not configuring the same device
                    await self.async_set_unique_id(
                        f"ecologi_{user_input[CONF_USERNAME]}"
                    )
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Ecologi ({user_input[CONF_USERNAME]})",
                        data=user_input,
                    )
            except NotFoundException:
                errors[CONF_USERNAME] = "invalid_username"
            else:
                errors[CONF_USERNAME] = "server_error"

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

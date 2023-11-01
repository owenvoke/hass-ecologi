from datetime import timedelta
import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from ecologi import Ecologi, NotFoundException

import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER: logging.Logger = logging.getLogger(__package__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
    }
)


class EcologiConfigFlow(ConfigFlow, domain=DOMAIN):
    """The configuration flow for an Ecologi system."""

    async def async_step_user(self, user_input=None) -> FlowResult:
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

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return EcologiOptionsFlowHandler(config_entry)


class EcologiOptionsFlowHandler(OptionsFlow):
    """Config flow options handler for Ecologi."""

    def __init__(self, config_entry: ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry
        # Cast from MappingProxy to dict to allow update.
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            self.options.update(user_input)
            coordinator = self.hass.data[DOMAIN][self.config_entry.entry_id]

            update_interval = timedelta(
                seconds=self.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            )

            _LOGGER.debug("Updating coordinator, update_interval: %s", update_interval)

            coordinator.update_interval = update_interval

            return self.async_create_entry(title="", data=self.options)

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )

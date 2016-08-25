"""
RESTful platform for notify component.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/notify.rest/
"""
import logging

import requests
import voluptuous as vol

from homeassistant.components.notify import (
    BaseNotificationService, PLATFORM_SCHEMA)
from homeassistant.const import CONF_RESOURCE
import homeassistant.helpers.config_validation as cv


CONF_EXPIRES = 'expires'
CONF_COLOR = 'color'
DEFAULT_EXPIRES = 15


color_dict = vol.All(
    vol.Schema({
        'red': vol.Coerce(int),
        'green': vol.Coerce(int),
        'blue': vol.Coerce(int),
    }),
)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_RESOURCE): cv.url,
    vol.Optional(CONF_EXPIRES, default=DEFAULT_EXPIRES): cv.positive_int,
    vol.Optional(CONF_COLOR, default={}): color_dict,
})


_LOGGER = logging.getLogger(__name__)


def get_service(hass, config):
    """Get the RESTful notification service."""
    resource = config.get(CONF_RESOURCE)
    expires = config.get(CONF_EXPIRES)
    color = config.get(CONF_COLOR)

    return TwolineNotificationService(
        resource, expires, color
    )


# pylint: disable=too-few-public-methods, too-many-arguments
class TwolineNotificationService(BaseNotificationService):
    """Implementation of a notification service for REST."""

    def __init__(self, resource, expires, color):
        """Initialize the service."""
        self._resource = resource
        self._expires = expires
        self._color = color

    def send_message(self, message="", **kwargs):
        """Send a message to a user."""
        data = {
            'message': message,
        }

        if self._color:
            data['color'] = [
                self._color['red'],
                self._color['green'],
                self._color['blue'],
            ]

        if self._expires:
            data['expires'] = self._expires

        response = requests.put(self._resource, json=data, timeout=10)

        if not response.ok:
            _LOGGER.exception(
                "Error sending message. Response %d: %s:",
                response.status_code, response.reason
            )

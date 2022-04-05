"""Self check."""

from __future__ import annotations

import logging
from typing import Final
import urllib.parse

from homeassistant.core import HomeAssistant
import homeassistant.components.persistent_notification as pn
from homeassistant.loader import async_get_integration

from .luci import LuciClient
from .const import DOMAIN

SELF_CHECK_METHODS: Final = {
    "misystem/status": "status",
    "xqnetwork/mode": "mode",
    "misystem/topo_graph": "topo_graph",
    "xqnetwork/wan_info": "wan_info",
    "misystem/led": "led",
    "xqnetwork/wifi_detail_all": "wifi_detail_all",
    "xqnetwork/wifi_connect_devices": "wifi_connect_devices",
    "misystem/devicelist": "device_list",
    "misystem/newstatus": "new_status",
}

_LOGGER = logging.getLogger(__name__)


async def async_self_check(hass: HomeAssistant, client: LuciClient, model: str) -> None:
    """Self check

    :param hass: HomeAssistant: HomeAssistant object
    :param client: LuciClient: Luci Client
    :param model: str: Router model
    """

    data = {
        "xqsystem/login": "🟢",
        "xqsystem/init_info": "🟢",
        "xqsystem/reboot": "🟢",
    }

    for code, method in SELF_CHECK_METHODS.items():
        action = getattr(client, method)

        if not action:
            data[code] = "🔴"

            continue

        try:
            await action()
            data[code] = "🟢"
        except BaseException:
            data[code] = "🔴"

    title: str = f"Router {client.ip} not supported.\n\nModel: {model}"

    message: str = "Check list:"

    for code, status in data.items():
        message += f"\n * {code}: {status}"

    integration = await async_get_integration(hass, DOMAIN)

    # fmt: off
    link: str = f"{integration.issue_tracker}/new?title=" \
        + urllib.parse.quote_plus(f"Add supports {model}") \
        + "&body=" \
        + urllib.parse.quote_plus(message)
    # fmt: on

    message = f"{title}\n\n{message}"
    message += f'\n\n <a href="{link}" target="_blank">Create an issue with the data from this post to add support</a>'

    pn.async_create(hass, message, "MiWifi")
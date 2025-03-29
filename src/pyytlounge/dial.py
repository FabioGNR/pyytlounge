"""Helper functions for discovering YouTube Lounge through DIAL"""

from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree
from aiohttp import ClientSession


@dataclass
class DialResult:
    """YouTube screen obtained using DIAL"""

    screen_name: str
    screen_id: str


DEVICE_NAMESPACE = "urn:schemas-upnp-org:device-1-0"
SERVICE_NAMESPACE = "urn:dial-multiscreen-org:schemas:dial"


def _get_optional_element_text(element: Optional[ElementTree.Element], default: str):
    if element:
        return element.text or default
    return default


async def get_screen_id_from_dial(url: str) -> Optional[DialResult]:
    """Tries to get YouTube screen id from a DIAL endpoint"""
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            headers = response.headers
            devices = ElementTree.fromstring(await response.text())

        friendly_name = devices.find(".//device/friendlyName", {"": DEVICE_NAMESPACE})
        app_url = headers["application-url"]
        youtube_url = app_url + "YouTube"
        async with session.get(youtube_url) as response:
            if response.status != 200:
                return None
            service = ElementTree.fromstring(await response.text())
        screen_id = service.find(".//additionalData/screenId", {"": SERVICE_NAMESPACE})
        if screen_id is not None and screen_id.text is not None:
            return DialResult(
                screen_name=_get_optional_element_text(friendly_name, ""),
                screen_id=screen_id.text,
            )
    return None

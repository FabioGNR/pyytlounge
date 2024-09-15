# pylint: disable=protected-access
import pytest
from pyytlounge import YtLoungeApi
from .devices import Device, devices


@pytest.mark.parametrize("device", devices.values(), ids=devices.keys())
def test_event_loungeStatus(api: YtLoungeApi, device: Device):
    api._process_event("loungeStatus", [device.data["loungeStatus"]])

    assert api._screen_name == device.expectations["screen_name"]
    assert api._device_info == device.expectations["device_info"]

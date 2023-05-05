import pytest
from pyytlounge import YtLoungeApi
from .devices import Device, devices


@pytest.mark.parametrize("device", devices.values(), ids=devices.keys())
def test_event_loungeStatus(wrapper: YtLoungeApi, device: Device):
    wrapper._process_event(1, "loungeStatus", [device.data["loungeStatus"]])

    assert wrapper._screen_name == device.expectations["screen_name"]
    assert wrapper._device_info == device.expectations["device_info"]

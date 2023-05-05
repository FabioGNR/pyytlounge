from typing import TypedDict, Dict
from dataclasses import dataclass


class DeviceData(TypedDict):
    loungeStatus: str


class DeviceExpectations(TypedDict):
    screen_name: str
    screen_device_name: str
    device_info: dict


@dataclass
class Device:
    data: DeviceData
    expectations: DeviceExpectations


devices: Dict[str, Device] = {
    "LG OLED55C7V": Device(
        {
            "loungeStatus": {
                "devices": """[
                {
                    "app": "lb-v4",
                    "capabilities": "dsp,mic,dpa,ntb,que,mus",
                    "clientName": "tvhtml5",
                    "experiments": "",
                    "name": "YouTube on TV",
                    "theme": "cl",
                    "id": "xxxxxx-xxxx-xxx-xxx-xxxxxxx",
                    "type": "LOUNGE_SCREEN",
                    "hasCc": "true",
                    "deviceInfo": "{\\"brand\\":\\"LG\\",\\"model\\":\\"OLED55C7V-Z\\",\\"year\\":0,\\"os\\":\\"webOS\\",\\"osVersion\\":\\"2017\\",\\"chipset\\":\\"M16P\\",\\"clientName\\":\\"TVHTML5\\",\\"dialAdditionalDataSupportLevel\\":\\"full\\",\\"mdxDialServerType\\":\\"MDX_DIAL_SERVER_TYPE_SYSTEM\\"}",
                    "receiverIdentityMatchStatus": "IS_RECEIVER"
                },
                {
                    "app": "android-phone-18.16.34",
                    "pairingType": "dial",
                    "capabilities": "que,dsdtr,atp,mus",
                    "clientName": "android",
                    "deviceContext": "{\\"user_agent\\":\\"com.google.android.youtube\\\\/18.16.34(Linux; U; Android 13; en_GB; SM-G991B Build\\\\/TP1A.220624.014)\\",\\"window_width_points\\":360,\\"window_height_points\\":758,\\"os_name\\":\\"Android\\",\\"ms\\":\\"xxxxxxxxxxxxxxxx\\"}",
                    "experiments": "",
                    "name": "SAMSUNG SM-G991B",
                    "theme": "cl",
                    "id": "xxxxxxxxxx",
                    "type": "REMOTE_CONTROL",
                    "receiverIdentityMatchStatus": "MATCHES_RECEIVER"
                },
                {
                    "app": "web",
                    "pairingType": "unknown",
                    "capabilities": "que,dsdtr,atp,mus",
                    "clientName": "unknown",
                    "deviceContext": "user_agent=dunno&window_width_points=&window_height_points=&os_name=android&ms=",
                    "experiments": "",
                    "name": "Test",
                    "theme": "cl",
                    "id": "xxxxxxxxxxx",
                    "type": "REMOTE_CONTROL",
                    "localChannelEncryptionKey": "xxxxxxxxxxxxxxx",
                    "receiverIdentityMatchStatus": "DOES_NOT_MATCH_RECEIVER"
                }]"""
            }
        },
        {
            "screen_name": "YouTube on TV",
            "screen_device_name": "LG OLED55C7V-Z",
            "device_info": {
                "brand": "LG",
                "model": "OLED55C7V-Z",
                "year": 0,
                "os": "webOS",
                "osVersion": "2017",
                "chipset": "M16P",
                "clientName": "TVHTML5",
                "dialAdditionalDataSupportLevel": "full",
                "mdxDialServerType": "MDX_DIAL_SERVER_TYPE_SYSTEM",
            },
        },
    ),
    "Nintendo Switch": Device(
        {
            "loungeStatus": {
                "devices": """[
                    {
                    "app": "lb-v4",
                    "capabilities": "dsp,mic,dpa,ntb,vsp,que,mus",
                    "clientName": "tvhtml5",
                    "experiments": "",
                    "name": "Nintendo Switch",
                    "theme": "cl",
                    "id": "XXXXXXXXXXXXXXXXXXX",
                    "type": "LOUNGE_SCREEN",
                    "hasCc": "true",
                    "receiverIdentityMatchStatus": "IS_RECEIVER"
                }]"""
            }
        },
        {
            "screen_name": "Nintendo Switch",
            "screen_device_name": None,
            "device_info": None,
        },
    ),
}

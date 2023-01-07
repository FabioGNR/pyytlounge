from time import sleep
import requests
from requests.models import PreparedRequest
import json
from typing import Tuple, Iterator
from enum import Enum
from variables import Variables
from api import api_base
import logging

device_name = 'pyytlounge'
screen_id = Variables.screen_id
lounge_token = Variables.lounge_token

# useful for extending support
print_unknown_events = False


# todo: replace with string enum with new python
class State(str, Enum):
    Stopped='-1',
    Paused='1',
    Playing='2',
    Starting='3', # unsure, only seen once


def parse_event_chunks(iter: Iterator[str]) -> Tuple[str, dict]:
    chunk_remaining = 0
    current_chunk = ''
    for line in iter:
        if line is not str: line = line.decode()
        if chunk_remaining <= 0:
            chunk_remaining = int(line)
            current_chunk = ''
        else:
            current_chunk = current_chunk + line
            chunk_remaining = chunk_remaining - len(line) - 1
            if chunk_remaining == 0:
                events = json.loads(current_chunk)
                yield events

def process_event(id, type, args):
    if type == "onStateChange" or type == "nowPlaying":
        data = args[0]
        if "state" in data:
            state = State(data["state"])
            print(f"New state {state}")
    elif print_unknown_events:
        print(f"{id} {type} {args}")


def process_events(events):
    sid, gsession = None, None
    for e in events:
        id, (type, *args) = e
        if type == "c":
            sid = args[0]
        elif type == "S":
            gsession = args[0]
        else:
            process_event(id, type, args)

    last_id = events[-1][0]
    return sid, gsession, last_id

def listen_events(SID, gsession, last_event_id):
    print(f"Start listening with {SID}, {gsession}, {last_event_id}")
    params = {
        'device': 'REMOTE_CONTROL',
        'name': device_name,
        'app': 'youtube-desktop',
        'loungeIdToken': lounge_token,
        'VER': '8',
        'v': '2',
        'RID': 'rpc',
        'SID': SID,
        'CI': '0',
        'AID': last_event_id,
        'gsessionid': gsession,
        'TYPE': 'xmlhttp',
    }
    req = PreparedRequest()
    req.prepare_url(f"{api_base}/bc/bind", params)
    res = requests.get(req.url, stream=True)

    for events in parse_event_chunks(res.iter_lines()):
        yield events

def connect():
    connect_body = {
        'app': 'web',
        'mdx-version': '3',
        'name': device_name,
        'id': screen_id,
        'device': "REMOTE_CONTROL",
        "capabilities":  "que,dsdtr,atp",
        "method":  "setPlaylist",
        "magnaKey":  "cloudPairedDevice",
        "ui":  "",
        "deviceContext": "user_agent=dunno&window_width_points=&window_height_points=&os_name=android&ms=",
        "theme":  "cl",
        'loungeIdToken': lounge_token
    }
    res = requests.post(f"{api_base}/bc/bind?RID=1&VER=8&CVER=1&auth_failure_option=send_error", data=connect_body)
    events = next(parse_event_chunks(iter(res.content.splitlines())))
    sid, gsession, last_id = process_events(events)

    if not sid or not gsession:
        raise Exception(f"Missing something: sid {sid} gsession {gsession}")
    while True:
        try:
            for events in listen_events(sid, gsession, last_id):
                n_sid, n_gsession, last_id = process_events(events)
                if n_sid != None:
                    sid = n_sid
                    print(f"New sid {sid}")
                if n_gsession != None:
                    gsession = n_gsession
                    print(f"New gsession {gsession}")
            if not sid or not gsession:
                raise Exception(f"Missing something: sid {sid} gsession {gsession}")
        except Exception:
            logging.exception("Exception while listening for events")
            sleep(2)


connect()
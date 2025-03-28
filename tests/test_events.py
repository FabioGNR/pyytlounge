from pyytlounge.events import NowPlayingEvent
from pyytlounge.lounge_models import _NowPlayingData
from pyytlounge.models import State


def test_empty_now_playing_event():
    data = _NowPlayingData({"listId": "RQhvB4xAAAAA-hYxOY"})
    event = NowPlayingEvent(data)

    assert event.video_id is None
    assert event.duration is None
    assert event.current_time is None
    assert event.state == State.Stopped

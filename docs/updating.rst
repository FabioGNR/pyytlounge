Updating
========

Migrate to event listener (v3.x.x)
----------------------------------

Previously, to receive events you'd pass in a callback to `subscribe()`. This has been replaced by a more flexible mechanism.

Before:

.. code-block:: python

    async def receive_state(state: PlaybackState):
        print(f"New state: {state}")

    await api.subscribe(receive_state)


After:

.. code-block:: python

    from pyytlounge import EventListener

    class CustomListener(EventListener):
        def __init__(self):
            self.last_video_id: Optional[str] = None

        async def playback_state_changed(self, event: PlaybackStateEvent) -> None:
            """Called when playback state changes (position, play/pause)"""
            print(
                f"New state: {event.state} = id: {self.last_video_id} pos: {event.current_time} duration: {event.duration}"
            )

        async def now_playing_changed(self, event: NowPlayingEvent) -> None:
            """Called when active video changes"""
            print(
                f"New state: {event.state} = id: {event.video_id} pos: {event.current_time} duration: {event.duration}"
            )
            self.last_video_id = event.video_id

    with YtLoungeApi("Some device", CustomListener()) as api:
        ...
        await api.subscribe()


By creating a subclass of `EventListener` you can override methods for each type of event you're interested in.

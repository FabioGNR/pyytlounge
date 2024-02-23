Usage
=====

Installation
------------

To use PyYtLounge, first install it using pip:

.. code-block:: console

    (.venv) $ pip install pyytlounge

Initialization
--------------

Create an instance of the :class:`pyytlounge.YtLoungeApi` class, which takes a device name and optionally a logger:

.. code-block:: python

    with YtLoungeApi('Test client') as api:
        ...

As you can see `with ...:` is used. The class is an asynchronous context manager as on close it needs to clean up the aiohttp session.
Alternatively, you can call `.close()` manually:

.. code-block:: python

    api = YtLoungeApi('test client')
    ...
    await api.close()


When we have an instance of the class, we need to :meth:`~.YtLoungeApi.pair` with a screen.
Currently this can only be done through a pairing code (this can be found in the app's settings).

.. code-block:: python

    pairing_code = input("Enter pairing code: ") # or from another source
    paired_and_linked = await api.pair(pairing_code)

If this succeeds the api is now in a linked state.
This means we have the two requirements to connect to a screen: the screen identifier and the lounge id token.
The screen identifier should remain the same, but the lounge id token can change.
If needed, you can refresh the lounge id token using :meth:`pyytlounge.YtLoungeApi.refresh_auth`:

.. code-block:: python

    linked = await api.refresh_auth()

From a linked state, the api is ready to :meth:`~.YtLoungeApi.connect`:

.. code-block:: python

    connected = await api.connect()

If this succeeds, commands can now be submitted, such as :meth:`~.YtLoungeApi.seek_to`:

.. code-block:: python

    # seek to 10 seconds
    seek_success = await api.seek_to(self, time=10)

You can also :meth:`~.YtLoungeApi.subscribe` to the screen's status:

.. code-block:: python

    def receive_state(state: State):
        print(state)

    # this will block until the subscription ends
    subscribed = await api.subscribe(receive_state)


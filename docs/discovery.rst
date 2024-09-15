Discovery
=====

DIAL
------------

PyYtLounge can get the screen id from a DIAL endpoint which allows for automatic discovery.
First you need to obtain the DIAL endpoint URL.

.. note::
    Discovering the DIAL endpoint is not a part of this library.
    This can be done using SSDP with a ST of `urn:dial-multiscreen-org:service:dial:1`.
    The DIAL endpoint will be the SSDP location.

Once you have the URL, call :meth:`pyytlounge.dial.get_screen_id_from_dial`:

.. code-block:: python

    from pyytlounge.dial import get_screen_id_from_dial

    dial_url = ...
    result = get_screen_id_from_dial(dial_url)
    async with YtLoungeApi('Test client') as api:
        paired = api.pair_with_screen_id(result.screen_id, result.screen_name)
        print(paired)

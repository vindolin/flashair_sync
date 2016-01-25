flashair_sync
-------------

Installation
------------

    pip install flashair_sync


Simple directory syncer for Toshiba Flashair SD cards, used in 3D printers.

Example usage
-------------

::

    $ flashair_sync /directory/with/x3g_files 192.168.178.70 x3g s3g


--help output
-------------

.. code-block::

    usage: __init__.py [-h] [-p POLL_INTERVAL]
                       directory_path flashair_address file_extensions
                       [file_extensions ...]

    Watch a directory for change/delete events to files and sync to flashair card
    (not recursive!).

    positional arguments:
      directory_path        The directory to watch for changes.
      flashair_address      The address of your flashair card, eg.
                            "192.168.178.41"
      file_extensions       Only files that match one of these extensions get
                            monitored.

    optional arguments:
      -h, --help            show this help message and exit
      -p POLL_INTERVAL, --poll_interval POLL_INTERVAL
                            How many seconds between directory polls.

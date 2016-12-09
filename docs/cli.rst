Command-line tool
=================

If you installed dottorrent using pip, ``dottorrent`` should be
available in your system path.

.. highlight:: none

::

	usage: dottorrent [-h] [--tracker TRACKER] [--web_seed WEB_SEED]
                  [--piece_size PIECE_SIZE] [--private] [--source SOURCE]
                  [--comment COMMENT] [--date DATE] [--md5] [--verbose]
                  path output_path

	Create a .torrent file

	positional arguments:
	  path                  path to file/directory to create torrent from
	  output_path           Output path for created .torrent file. If a directory
	                        is provided, the filename will be automatically
	                        generated based on the input.

	optional arguments:
	  -h, --help            show this help message and exit
	  --tracker TRACKER, -t TRACKER
	                        tracker URL (can be specified multiple times)
	  --web_seed WEB_SEED, -w WEB_SEED
	                        web seed URL (can be specified multiple times)
	  --piece_size PIECE_SIZE, -s PIECE_SIZE
	                        piece size in bytes
	  --private, -p         set private flag
	  --source SOURCE       source string (useful for private trackers)
	  --comment COMMENT, -c COMMENT
	                        string for the torrent comment field
	  --date DATE, -d DATE  Torrent creation date. Valid values: unix
	                        timestamp/none/now (default: now)
	  --md5                 Add per-file MD5 hashes
	  --verbose, -v         verbose mode

	dottorrent/1.6.0 (https://github.com/kz26/dottorrent)


To add multiple trackers and/or web seeds, repeat the ``-t`` and ``-w`` as many times as necessary,
e.g. ``-t tracker1 -t tracker2``.


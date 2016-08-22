Command-line tool
=================

.. highlight:: none

::

	usage: dottorrent_cli.py [-h] [--tracker TRACKERS] [--http_seed HTTP_SEEDS]
	                         [--piece_size PIECE_SIZE] [--private]
	                         [--comment COMMENT] [--date DATE] [--md5] [--verbose]
	                         path output_path

	Create a .torrent file

	positional arguments:
	  path                  path to file/directory to create torrent from
	  output_path           path to save .torrent file to

	optional arguments:
	  -h, --help            show this help message and exit
	  --tracker TRACKERS, -t TRACKERS
	                        tracker URL (can be specified multiple times)
	  --http_seed HTTP_SEEDS, -w HTTP_SEEDS
	                        HTTP seed URL (can be specified multiple times)
	  --piece_size PIECE_SIZE, -s PIECE_SIZE
	                        piece size in bytes
	  --private, -p         set private flag
	  --comment COMMENT, -c COMMENT
	                        free-text string for the torrent comment field
	  --date DATE, -d DATE  Torrent creation date (unix timestamp)
	  --md5                 Add per-file MD5 hashes
	  --verbose, -v         verbose mode

	dottorrent/1.0.0 (https://github.com/kz26/dottorrent)

Command-line tool
=================

If you installed dottorrent using pip, ``dottorrent`` should be
available in your system path.

.. highlight:: none

::

	usage: dottorrent [-h] [--tracker TRACKER] [--web_seed WEB_SEED]
                  [--piece_size PIECE_SIZE] [--private] [--source SOURCE]
                  [--exclude RE] [--comment COMMENT] [--date DATE] [--md5]
                  [--verbose]
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
							piece size, e.g. 16KB, 1M. Leave unspecified for
							automatic piece size
	--private, -p         set private flag (useful for private trackers)
	--source SOURCE       source string (useful for private trackers)
	--exclude RE, -x RE   filename patterns that should be excluded (can be
							specified multiple times)
	--comment COMMENT, -c COMMENT
							string for the torrent comment field
	--date DATE, -d DATE  Torrent creation date. Valid values: unix
							timestamp/none/now (default: now)
	--md5                 Add per-file MD5 hashes
	--verbose, -v         verbose mode

	dottorrent/1.8.0 (https://github.com/kz26/dottorrent)


When creating a torrent, all dotfiles (filenames beginning with a '.') are excluded. On Windows systems running Python 3.5+, all hidden files are excluded as well.

To add multiple trackers, web seeds and/or exclusion patterns, repeat the ``-t``, ``-w``, or ``-x`` as many times as necessary,
e.g. ``-t tracker1 -t tracker2`` or ``-x "*.jpg" --exclude "*.png"``.


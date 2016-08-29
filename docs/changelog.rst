Changelog
=========

1.4.2
-----
* Rename dottorrent_cli.py to dottorrent_cli

1.4.1
-----
* Ignore empty files in get_info() and generate()

1.4.0
-----
* Use custom exceptions (see exceptions.py)
* Add check for empty input

1.3.0
-----
* Unicode support

1.2.2
-----
* Fix auto piece sizing in generate() with small files 

1.2.0
-----
* Switch to BEP 19 (GetRight style) web seeds

1.1.1
-----
* Return True/False in generate()

1.1.0
-----
* Move include_md5 option to Torrent constructor
* Add cancellation functionality to generate function via existing callback
* get_info() now always scans/rescans the input path instead of checking for cached data
* Documentation improvements

1.0.2
-----
* Raise exception when path is a directory and no files exist

1.0.1
-----
* Change bencoder.pyx minimum version dependency to 1.1.1
* Add none/now to CLI date option
* Minor tweaks


1.0.0
-----
* Initial release.
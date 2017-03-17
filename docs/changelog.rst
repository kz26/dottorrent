Changelog
=========

1.8.0
-----
* Human-friendly piece size specification in CLI
* Minor string formatting improvements

1.7.0
-----
* Implement filename pattern exclusion from PR #7 (--exclude, -x)

1.6.0
-----
* Add support for source strings (--source option)
* Exclude hidden dotfiles from being added
* Exclude hidden files on Windows (requires Python 3.5+)
* Refactor - CLI tool is now simply `dottorrent`

1.5.3
-----
* Use relative paths instead of absolute paths for directory mode path generation
* Add invalid input path check in get_info() and generate()

1.5.2
-----
* Use humanfriendly.format_size in binary mode
* Pin major versions of dependencies in requirements.txt and setup.py

1.5.1
-----
* Fix filename clobbering when filename contains parent path string (issue #2)

1.5.0
-----
* Allow both file and directory names to be specified for output_path (PR #1, @mahkitah)

1.4.3
-----
* dottorrent_cli: Change output_path to output_file for clarity

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

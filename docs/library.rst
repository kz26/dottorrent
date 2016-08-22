Library
=======

The dottorrent library can be used in a Python script or program to create .torrent files.

.. autoclass:: dottorrent.Torrent
   :members:
   :undoc-members:

Example Usage
-------------
::

	from dottorrent import Torrent

	t = Torrent('/my/data/', trackers=['http://tracker.openbittorrent.com:80/announce'])
	t.generate()
	with open('mydata.torrent', 'wb') as f:
		t.save(f)
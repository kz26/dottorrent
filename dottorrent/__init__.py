# MIT License

# Copyright (c) 2016 Kevin Zhang

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from base64 import b32encode
from collections import OrderedDict
from datetime import datetime
from hashlib import sha1, md5
import fnmatch
import math
import os
import sys
from urllib.parse import urlparse

from bencoder import bencode

from .version import __version__
from . import exceptions

DEFAULT_CREATOR = "dottorrent/{} (https://github.com/kz26/dottorrent)".format(
    __version__)


MIN_PIECE_SIZE = 2 ** 14
MAX_PIECE_SIZE = 2 ** 22


if sys.version_info >= (3, 5) and os.name == 'nt':
    import stat

    def is_hidden_file(path):
        fn = path.split(os.sep)[-1]
        return fn.startswith('.') or \
            bool(os.stat(path).st_file_attributes &
                 stat.FILE_ATTRIBUTE_HIDDEN)
else:
    def is_hidden_file(path):
        fn = path.split(os.sep)[-1]
        return fn.startswith('.')


def print_err(v):
    print(v, file=sys.stderr)


class Torrent(object):

    def __init__(self, path, trackers=None, web_seeds=None,
                 piece_size=None, private=False, source=None,
                 creation_date=None, comment=None, created_by=None,
                 include_md5=False, exclude=None):
        """
        :param path: path to a file or directory from which to create the torrent
        :param trackers: list/iterable of tracker URLs
        :param web_seeds: list/iterable of HTTP/FTP seed URLs
        :param piece_size: Piece size in bytes. Must be >= 16 KB and a power of 2.
            If None, ``get_info()`` will be used to automatically select a piece size.
        :param private: The private flag. If True, DHT/PEX will be disabled.
        :param source: An optional source string for the torrent.
        :param exclude: A list of filename patterns that should be excluded from the torrent.
        :param creation_date: An optional datetime object representing the torrent creation date.
        :param comment: An optional comment string for the torrent.
        :param created_by: name/version of the program used to create the .torrent.
            If None, defaults to the value of ``DEFAULT_CREATOR``.
        :param include_md5: If True, also computes and stores MD5 hashes for each file.
        """

        self.path = os.path.normpath(path)
        self.trackers = trackers
        self.web_seeds = web_seeds
        self.piece_size = piece_size
        self.private = private
        self.source = source
        self.exclude = [] if exclude is None else exclude
        self.creation_date = creation_date
        self.comment = comment
        self.created_by = created_by
        self.include_md5 = include_md5

    @property
    def trackers(self):
        return self._trackers

    @trackers.setter
    def trackers(self, value):
        tl = []
        if value:
            for t in value:
                pr = urlparse(t)
                if pr.scheme and pr.netloc:
                    tl.append(t)
                else:
                    raise exceptions.InvalidURLException(t)
        self._trackers = tl

    @property
    def web_seeds(self):
        return self._web_seeds

    @web_seeds.setter
    def web_seeds(self, value):
        tl = []
        if value:
            for t in value:
                pr = urlparse(t)
                if pr.scheme and pr.netloc:
                    tl.append(t)
                else:
                    raise exceptions.InvalidURLException(t)
        self._web_seeds = tl

    @property
    def piece_size(self):
        return self._piece_size

    @piece_size.setter
    def piece_size(self, value):
        if value:
            value = int(value)
            if value > 0 and (value & (value-1) == 0):
                if value < MIN_PIECE_SIZE:
                    raise exceptions.InvalidPieceSizeException(
                        "Piece size should be at least 16 KB")
                if value > MAX_PIECE_SIZE:
                    print_err("Warning: piece size is greater than 4 MB")
                self._piece_size = value
            else:
                raise exceptions.InvalidPieceSizeException(
                    "Piece size must be a power of 2")
        else:
            self._piece_size = None

    def get_info(self):
        """
        Scans the input path and automatically determines the optimal
        piece size (up to 4 MB), along with other basic info such
        as the total size and the total number of files. If ``piece_size``
        has already been set, the custom value will be used instead.

        :return: ``(total_size, total_files, piece_size, num_pieces)``
        """
        if os.path.isfile(self.path):
            total_size = os.path.getsize(self.path)
            total_files = 1
        elif os.path.exists(self.path):
            total_size = 0
            total_files = 0
            for x in os.walk(self.path):
                for fn in x[2]:
                    if any(fnmatch.fnmatch(fn, ext) for ext in self.exclude):
                        continue
                    fpath = os.path.normpath(os.path.join(x[0], fn))
                    fsize = os.path.getsize(fpath)
                    if fsize and not is_hidden_file(fpath):
                        total_size += fsize
                        total_files += 1
        else:
            raise exceptions.InvalidInputException
        if not (total_files and total_size):
            raise exceptions.EmptyInputException
        if self.piece_size:
            ps = self.piece_size
        else:
            ps = 1 << max(0, math.ceil(math.log(total_size / 1500, 2)))
            if ps < MIN_PIECE_SIZE:
                ps = MIN_PIECE_SIZE
            if ps > MAX_PIECE_SIZE:
                ps = MAX_PIECE_SIZE
        return (total_size, total_files, ps, math.ceil(total_size / ps))

    def generate(self, callback=None):
        """
        Computes and stores piece data. Returns ``True`` on success, ``False``
        otherwise.

        :param callback: progress/cancellation callable with method
            signature ``(filename, pieces_completed, pieces_total)``.
            Useful for reporting progress if dottorrent is used in a
            GUI/threaded context, and if torrent generation needs to be cancelled.
            The callable's return value should evaluate to ``True`` to trigger
            cancellation.
        """
        files = []
        single_file = os.path.isfile(self.path)
        if single_file:
            files.append((self.path, os.path.getsize(self.path), {}))
        elif os.path.exists(self.path):
            for x in os.walk(self.path):
                for fn in x[2]:
                    if any(fnmatch.fnmatch(fn, ext) for ext in self.exclude):
                        continue
                    fpath = os.path.normpath(os.path.join(x[0], fn))
                    fsize = os.path.getsize(fpath)
                    if fsize and not is_hidden_file(fpath):
                        files.append((fpath, fsize, {}))
        else:
            raise exceptions.InvalidInputException
        total_size = sum([x[1] for x in files])
        if not (len(files) and total_size):
            raise exceptions.EmptyInputException
        # set piece size if not already set
        if self.piece_size is None:
            self.piece_size = self.get_info()[2]
        if files:
            self._pieces = bytearray()
            i = 0
            num_pieces = math.ceil(total_size / self.piece_size)
            pc = 0
            buf = bytearray()
            while i < len(files):
                fe = files[i]
                f = open(fe[0], 'rb')
                if self.include_md5:
                    md5_hasher = md5()
                else:
                    md5_hasher = None
                for chunk in iter(lambda: f.read(self.piece_size), b''):
                    buf += chunk
                    if len(buf) >= self.piece_size \
                            or i == len(files)-1:
                        piece = buf[:self.piece_size]
                        self._pieces += sha1(piece).digest()
                        del buf[:self.piece_size]
                        pc += 1
                        if callback:
                            cancel = callback(fe[0], pc, num_pieces)
                            if cancel:
                                f.close()
                                return False
                    if self.include_md5:
                        md5_hasher.update(chunk)
                if self.include_md5:
                    fe[2]['md5sum'] = md5_hasher.hexdigest()
                f.close()
                i += 1
            # Add pieces from any remaining data
            while len(buf):
                piece = buf[:self.piece_size]
                self._pieces += sha1(piece).digest()
                del buf[:self.piece_size]
                pc += 1
                if callback:
                    cancel = callback(fe[0], pc, num_pieces)
                    if cancel:
                        return False

        # Create the torrent data structure
        data = OrderedDict()
        if len(self.trackers) == 1:
            data['announce'] = self.trackers[0].encode()
        elif len(self.trackers) > 1:
            data['announce-list'] = [[x.encode()] for x in self.trackers]
        if self.comment:
            data['comment'] = self.comment.encode()
        if self.created_by:
            data['created by'] = self.created_by.encode()
        else:
            data['created by'] = DEFAULT_CREATOR.encode()
        if self.creation_date:
            data['creation date'] = int(self.creation_date.timestamp())
        if self.web_seeds:
            data['url-list'] = [x.encode() for x in self.web_seeds]
        data['info'] = OrderedDict()
        if single_file:
            data['info']['length'] = files[0][1]
            if self.include_md5:
                data['info']['md5sum'] = files[0][2]['md5sum']
            data['info']['name'] = files[0][0].split(os.sep)[-1].encode()
        else:
            data['info']['files'] = []
            path_sp = self.path.split(os.sep)
            for x in files:
                fx = OrderedDict()
                fx['length'] = x[1]
                if self.include_md5:
                    fx['md5sum'] = x[2]['md5sum']
                fx['path'] = [y.encode()
                              for y in x[0].split(os.sep)[len(path_sp):]]
                data['info']['files'].append(fx)
            data['info']['name'] = path_sp[-1].encode()
        data['info']['pieces'] = bytes(self._pieces)
        data['info']['piece length'] = self.piece_size
        data['info']['private'] = int(self.private)
        if self.source:
            data['info']['source'] = self.source.encode()

        self._data = data
        return True

    @property
    def info_hash_base32(self):
        """
        Returns the base32 info hash of the torrent. Useful for generating
        magnet links.

        .. note:: ``generate()`` must be called first.
        """
        if getattr(self, '_data', None):
            return b32encode(sha1(bencode(self._data['info'])).digest())
        else:
            raise exceptions.TorrentNotGeneratedException

    @property
    def info_hash(self):
        """
        :return: The SHA-1 info hash of the torrent. Useful for generating
            magnet links.

        .. note:: ``generate()`` must be called first.
        """
        if getattr(self, '_data', None):
            return sha1(bencode(self._data['info'])).hexdigest()
        else:
            raise exceptions.TorrentNotGeneratedException

    def dump(self):
        """
        :return: The bencoded torrent data as a byte string.

        .. note:: ``generate()`` must be called first.
        """
        if getattr(self, '_data', None):

            return bencode(self._data)
        else:
            raise exceptions.TorrentNotGeneratedException

    def save(self, fp):
        """
        Saves the torrent to ``fp``, a file(-like) object
        opened in binary writing (``wb``) mode.

        .. note:: ``generate()`` must be called first.
        """
        fp.write(self.dump())

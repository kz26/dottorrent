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
import math
import os
import sys
from urllib.parse import urlparse

from bencoder import bencode

from .version import __version__

DEFAULT_CREATOR = "dottorrent/{} (https://github.com/kz26/dottorrent)".format(
    __version__)


MIN_PIECE_SIZE = 2 ** 14
MAX_PIECE_SIZE = 2 ** 22


def print_err(v):
    print(v, file=sys.stderr)


class Torrent(object):

    def __init__(self, path, trackers=None, http_seeds=None,
                 piece_size=None, private=False, creation_date=None,
                 comment=None, created_by=None):
        """
        :param path: path to a file or directory from which to create the torrent
        :param trackers: list/iterable of tracker URLs
        :param http_seeds: list/iterable of HTTP seed URLs
        :param piece_size: Piece size in bytes. Must be >= 16 KB and a power of 2.
            If None, :code:`get_info()` will be used to automatically select a piece size.
        :param private: The private flag. If True, DHT/PEX will be disabled.
        :param creation_date: An optional datetime object representing the torrent creation date.
        :param comment: An optional comment string for the torrent.
        :param created_by: name/version of the program used to create the .torrent.
            If None, defaults to the value of :code:`DEFAULT_CREATOR`.
        """

        self.path = os.path.normpath(path)
        self.trackers = trackers
        self.http_seeds = http_seeds
        self.piece_size = piece_size
        self.private = private
        self.creation_date = creation_date
        self.comment = comment
        self.created_by = created_by

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
                    raise Exception("{} is not a valid URL".format(t))
        self._trackers = tl

    @property
    def http_seeds(self):
        return self._http_seeds

    @http_seeds.setter
    def http_seeds(self, value):
        tl = []
        if value:
            for t in value:
                pr = urlparse(t)
                if pr.scheme and pr.netloc:
                    tl.append(t)
                else:
                    raise Exception("{} is not a valid URL".format(t))
        self._http_seeds = tl

    @property
    def piece_size(self):
        return self._piece_size

    @piece_size.setter
    def piece_size(self, value):
        if value:
            value = int(value)
            if value > 0 and (value & (value-1) == 0):
                if value < MIN_PIECE_SIZE:
                    raise Exception("Piece size should be at least 16 KB")
                if value > MAX_PIECE_SIZE:
                    print_err("Warning: piece size is greater than 4 MB")
                self._piece_size = value
            else:
                raise Exception("Piece size must be a power of 2")
        else:
            self._piece_size = None

    def get_info(self):
        """
        Scans the input path and automatically determines the optimal
        piece size (up to 4 MB), along with other basic info such
        as the total size and the total number of files.

        :return: :code:`(total_size, total_files, piece_size, num_pieces)`
        """
        if getattr(self, '_files', None):
            total_size = sum([x[1] for x in self._files])
            total_files = len(self._files)
        elif os.path.isfile(self.path):
            total_size = os.path.getsize(self.path)
            total_files = 1
        else:
            total_size = 0
            total_files = 0
            for x in os.walk(self.path):
                for fn in x[2]:
                    fpath = os.path.normpath(os.path.join(x[0], fn))
                    total_size += os.path.getsize(fpath)
                    total_files += 1
        if self.piece_size:
            ps = self.piece_size
        else:
            ps = 1 << math.ceil(math.log(total_size / 1500, 2))
            if ps < MIN_PIECE_SIZE:
                ps = MIN_PIECE_SIZE
            if ps > MAX_PIECE_SIZE:
                ps = MAX_PIECE_SIZE
        return (total_size, total_files, ps, math.ceil(total_size / ps))

    def generate(self, include_md5=False, callback=None):
        """
        Computes and stores piece data.

        :param include_md5: If True, also computes and stores MD5 hashes for each file.
        :param callback: progress callable with method signature :code:`(filename, pieces_completed, pieces_total)`
        """
        self._files = []
        self._include_md5 = include_md5
        self._single_file = os.path.isfile(self.path)
        if self._single_file:
            self._files.append((self.path, os.path.getsize(self.path), {}))
        else:
            for x in os.walk(self.path):
                for fn in x[2]:
                    fpath = os.path.normpath(os.path.join(x[0], fn))
                    fsize = os.path.getsize(fpath)
                    self._files.append((fpath, fsize, {}))
        total_size = sum([x[1] for x in self._files])
        # set piece size if not already set
        if self.piece_size is None:
            self.piece_size = self.get_info()[2]
        if self._files:
            self._pieces = bytearray()
            i = 0
            num_pieces = math.ceil(total_size / self.piece_size)
            pc = 0
            buf = bytearray()
            while i < len(self._files):
                fe = self._files[i]
                f = open(fe[0], 'rb')
                if include_md5:
                    md5_hasher = md5()
                else:
                    md5_hasher = None
                for chunk in iter(lambda: f.read(self.piece_size), b''):
                    buf += chunk
                    if len(buf) >= self.piece_size \
                            or i == len(self._files)-1:
                        piece = buf[:self.piece_size]
                        self._pieces += sha1(piece).digest()
                        del buf[:self.piece_size]
                        pc += 1
                        if callback:
                            callback(fe[0], pc, num_pieces)
                    if include_md5:
                        md5_hasher.update(chunk)
                if include_md5:
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
                    callback(fe[0], pc, num_pieces)

        # Create the torrent data structure
        data = OrderedDict()
        if len(self.trackers) == 1:
            data['announce'] = self.trackers[0]
        elif len(self.trackers) > 1:
            data['announce-list'] = [[x] for x in self.trackers]
        if self.comment:
            data['comment'] = self.comment
        if self.created_by:
            data['created by'] = self.created_by
        else:
            data['created by'] = DEFAULT_CREATOR
        if self.creation_date:
            data['creation date'] = int(self.creation_date.timestamp())
        if self.http_seeds:
            data['httpseeds'] = self.http_seeds
        data['info'] = OrderedDict()
        if self._single_file:
            data['info']['length'] = self._files[0][1]
            if self._include_md5:
                data['info']['md5sum'] = self._files[0][2]['md5sum']
            data['info']['name'] = self._files[0][0].split(os.sep)[-1]
        else:
            data['info']['files'] = []
            for x in self._files:
                fx = OrderedDict()
                fx['length'] = x[1]
                if self._include_md5:
                    fx['md5sum'] = x[2]['md5sum']
                fx['path'] = x[0].replace(self.path, '')[1:].split(os.sep)
                data['info']['files'].append(fx)
            data['info']['name'] = self.path.split(os.sep)[-1]
        data['info']['pieces'] = bytes(self._pieces)
        data['info']['piece length'] = self.piece_size
        data['info']['private'] = int(self.private)

        self._data = data

    @property
    def info_hash_base32(self):
        """
        Returns the base32 info hash of the torrent. Useful for generating
        magnet links.

        .. note:: :code:`generate()` must be called first.
        """
        if getattr(self, '_data', None):
            return b32encode(sha1(bencode(self._data['info'])).digest())
        else:
            raise Exception(
                "Torrent not generated - call generate() first")

    @property
    def info_hash(self):
        """
        :return: The SHA-1 info hash of the torrent. Useful for generating
            magnet links.

        .. note:: :code:`generate()` must be called first.
        """
        if getattr(self, '_data', None):
            return sha1(bencode(self._data['info'])).hexdigest()
        else:
            raise Exception(
                "Torrent not generated - call generate() first")

    def dump(self):
        """
        :return: The bencoded torrent data as a byte string.

        .. note:: :code:`generate()` must be called first.
        """
        if getattr(self, '_data', None):

            return bencode(self._data)
        else:
            raise Exception(
                "Torrent not generated - call generate() first")

    def save(self, fp):
        """
        Saves the torrent to :code:`fp`, a file(-like) object
        opened in binary writing (``wb``) mode.

        .. note:: :code:`generate()` must be called first.
        """
        fp.write(self.dump())



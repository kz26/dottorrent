#!/usr/bin/env python3

from hashlib import sha1, md5
import math
import os
import sys
from urllib.parse import urlparse

from bencoder import bencode

MIN_PIECE_SIZE = 2 ** 14
MAX_PIECE_SIZE = 2 ** 22


class Torrent(object):

    def __init__(self, path, trackers=None, http_seeds=None,
                 piece_size=None, private=False, creation_date=None,
                 comment=None, created_by=None):

        self.path = path
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
                    sys.stderr.write(
                        "Warning: piece size is greater than 4 MB\n")
                self._piece_size = value
            else:
                raise Exception("Piece size must be a power of 2")
        else:
            self._piece_size = None

    def generate(self, include_md5=False):
        self._files = []
        if os.path.isfile(self.path):
            self._files.append((self.path, os.path.getsize(self.path)))
        else:
            for x in os.walk(self.path):
                for fn in x[2]:
                    fpath = os.path.normpath(os.path.join(x[0], fn))
                    fsize = os.path.getsize(fpath)
                    self._files.append((fpath, fsize, {}))
        total_size = sum([x[1] for x in self._files])
        # set piece size if not already set
        if self.piece_size is None:
            ps = 1 << math.ceil(math.log(total_size / 1500, 2))
            if ps < MIN_PIECE_SIZE:
                ps = MIN_PIECE_SIZE
            if ps > MAX_PIECE_SIZE:
                ps = MAX_PIECE_SIZE
            self.piece_size = ps
        if self._files:
            self._pieces = bytearray()
            i = 0
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
                    if include_md5:
                        md5_hasher.update(chunk)
                if include_md5:
                    fe[2]['md5sum'] = md5_hasher.hexdigest()
                i += 1

    def save(self):
        pass

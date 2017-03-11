#!/usr/bin/env python3

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

import argparse
import os.path
from datetime import datetime

from humanfriendly import format_size
from tqdm import tqdm

import dottorrent


def main():
    parser = argparse.ArgumentParser(description='Create a .torrent file',
                                     epilog=dottorrent.DEFAULT_CREATOR)
    parser.add_argument('--tracker', '-t', action='append', dest='trackers',
                        metavar='TRACKER',
                        help='tracker URL (can be specified multiple times)')
    parser.add_argument(
        '--web_seed', '-w', action='append', dest='web_seeds',
        metavar='WEB_SEED',
        help='web seed URL (can be specified multiple times)')
    parser.add_argument(
        '--piece_size', '-s', type=int, help='piece size in bytes')
    parser.add_argument(
        '--private', '-p', action='store_true', help='set private flag')
    parser.add_argument(
        '--source', help='source string (useful for private trackers)')
    parser.add_argument(
        '--exclude', '-x', help='filename patterns that should be excluded '
        '(can be specified multiple times)', action='append', dest='exclude',
        metavar='RE', default=[])
    parser.add_argument('--comment', '-c',
                        help='string for the torrent comment field')
    parser.add_argument('--date', '-d', default='now',
                        help='Torrent creation date. '
                        'Valid values: unix timestamp/none/now (default: now)')
    parser.add_argument(
        '--md5', action='store_true', help='Add per-file MD5 hashes')
    parser.add_argument(
        '--verbose', '-v', action='count', default=0, help='verbose mode')
    parser.add_argument(
        'path', help='path to file/directory to create torrent from')
    parser.add_argument(
        'output_path', help='Output path for created .torrent file. '
        'If a directory is provided, the filename will be automatically'
        'generated based on the input.')
    args = parser.parse_args()

    if args.date:
        if args.date.isdigit():
            creation_date = datetime.utcfromtimestamp(float(args.date))
        elif args.date.lower() == 'none':
            creation_date = None
        elif args.date.lower() == 'now':
            creation_date = datetime.now()

    print(dottorrent.DEFAULT_CREATOR)
    print("Input: {}".format(args.path))
    t = dottorrent.Torrent(args.path,
                           trackers=args.trackers,
                           web_seeds=args.web_seeds,
                           piece_size=args.piece_size,
                           private=args.private,
                           comment=args.comment,
                           creation_date=creation_date,
                           include_md5=args.md5,
                           source=args.source,
                           exclude=args.exclude,
                           )
    t_info = t.get_info()
    print("Files: {}".format(t_info[1]))
    print("Total size: {}".format(format_size(t_info[0], binary=True)))
    print("Piece size: {}".format(format_size(t_info[2], binary=True)))
    print("Pieces: {}".format(t_info[3]))
    print("MD5 hashing: {}".format(args.md5))
    for x in t.trackers:
        print("Tracker: " + x)
    for x in t.web_seeds:
        print("Web seed: " + x)
    print("Private torrent: {}".format(args.private))
    if args.comment:
        print("Comment: " + t.comment)
    if creation_date:
        print("Creation date: {}".format(creation_date))
    if args.source:
        print("Source: " + t.source)
    if args.exclude:
        print("Excluded: {}".format(', '.join(t.exclude)))

    pbar = tqdm(
        total=t_info[2] * t_info[3] / 1048576,
        unit=' MB', disable=args.verbose > 1)
    files = set()

    def progress_callback(fn, pieces_completed, total_pieces):
        if args.verbose == 1:
            if fn not in files:
                print(fn)
                files.add(fn)
        elif args.verbose > 1:
            print("{}/{} {}".format(pieces_completed, total_pieces, fn))
        pbar.update(t_info[2] / 1048576)

    t.generate(callback=progress_callback)
    pbar.close()

    output_path = os.path.normpath(args.output_path)
    if os.path.isdir(output_path):
        path_base = os.path.splitext(os.path.basename(t.path))[0]
        save_fn = os.path.join(args.output_path, path_base + '.torrent')
    else:
        save_fn = args.output_path

    with open(save_fn, 'wb') as f:
        t.save(f)
    print("Info hash: " + t.info_hash)
    print("Torrent file saved to {}".format(save_fn))


if __name__ == '__main__':
    main()

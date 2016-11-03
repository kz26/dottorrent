class EmptyInputException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__('Input path must be non-empty')


class InvalidInputException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__('Input path is invalid')


class InvalidURLException(Exception):

    def __init__(self, url, *args, **kwargs):
        super().__init__("{} is not a valid URL".format(url))


class InvalidPieceSizeException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TorrentNotGeneratedException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__('Torrent not generated - call generate() first')

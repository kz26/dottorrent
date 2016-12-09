from setuptools import setup, find_packages

with open('dottorrent/version.py') as f:
    exec(f.read())

setup(
    name="dottorrent",
    version=__version__,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dottorrent = dottorrent.cli:main'
        ]
    },

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['bencoder.pyx>=1.1.1,<2.0.0',
                      'humanfriendly>=2.1,<3.0', 'tqdm>=4.8.4,<5.0.0'],

    # metadata for upload to PyPI
    author="Kevin Zhang",
    author_email="kevin@kevinzhang.me",
    description="High-level Python 3 library and CLI tool for creating .torrent files",
    long_description=open('README.rst').read(),
    keywords="bittorrent torrent bencode",
    url="https://github.com/kz26/dottorrent",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)

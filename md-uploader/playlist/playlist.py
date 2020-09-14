from os import listdir
from pathlib import Path, PureWindowsPath
import shutil
import re

from tinytag import TinyTag


__SUPPORTED_PLAYLIST_EXTENSIONS = ['.m3u', '.m3u8']


class Playlist(object):
    def __init__(self, music_path, supported_extensions, playlist_path):
        self.__playlist_path = Path(playlist_path)
        self.__music_path = Path(music_path)
        self.__path_regex = re.compile(
            '(.*\\.(%s))' % '|'.join(supported_extensions),
            flags=re.IGNORECASE
        )

        track_paths = self.__parse_file_paths()
        self.__tracks = [Track(track_path) for track_path in track_paths]

    def __parse_file_paths(self):
        with self.__playlist_path.open() as file:
            contents = file.read()
            track_paths = [self.__create_path(match[0]) for match in self.__path_regex.findall(contents)]
            return [self.__music_path.joinpath(*track_path.parts[1:]) for track_path in track_paths]

    def __create_path(self, path):
        return PureWindowsPath(path)

    def count(self):
        return len(self.__tracks)

    def title(self):
        return self.__playlist_path.stem

    def duration(self):
        return sum([track.duration for track in self.__tracks])

    def is_single_artist(self):
        return len(set([track.artist for track in self.__tracks])) == 1

    def __iter__(self):
        for track in self.__tracks:
            yield track


class Track(object):
    def __init__(self, path):
        self.path = path
        tag = TinyTag.get(path)
        self.title = tag.title
        self.artist = tag.artist
        self.duration = tag.duration


def find_next_playlist_path_name(playlist_directory_path_name):
    playlist_directory_path = Path(playlist_directory_path_name)

    def is_playlist_file(playlist_path):
        return playlist_path.is_file() and playlist_path.suffix.lower() in __SUPPORTED_PLAYLIST_EXTENSIONS

    return next(
        (str(file_path) for file_path in playlist_directory_path.iterdir() if is_playlist_file(file_path)),
        ''
    )


def archive_playlist(playlist_path_name, archive_directory_path_name):
    playlist_path = Path(playlist_path_name)
    archive_directory_path = Path(archive_directory_path_name)

    shutil.move(
        playlist_path_name,
        archive_directory_path.joinpath(playlist_path.name)
    )

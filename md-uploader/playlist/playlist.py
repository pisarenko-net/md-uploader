from pathlib import Path, PureWindowsPath
import re

from tinytag import TinyTag



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
        return sum([track.duration() for track in self.__tracks])

    def is_single_artist(self):
        return len(set([track.artist() for track in self.__tracks])) == 1

    def __iter__(self):
        for track in self.__tracks:
            yield track


class Track(object):
    def __init__(self, path):
        self.path = path
        self.__tag = TinyTag.get(path)

    def title(self):
        return self.__tag.title

    def artist(self):
        return self.__tag.artist

    def duration(self):
        return self.__tag.duration

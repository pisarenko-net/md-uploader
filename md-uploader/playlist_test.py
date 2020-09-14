from playlist import Playlist
from transcode import create_pcm


PATH_MUSIC = '/mnt/music'
SUPPORTED_EXTENSIONS = ['flac']

playlist = Playlist(PATH_MUSIC, SUPPORTED_EXTENSIONS, '/mnt/music/_minidisc_queue/test.m3u8')

print(playlist.count())
print(playlist.title())
print(playlist.duration())
print(playlist.is_single_artist())

for track in playlist:
	print(track.path)
	print(track.duration)
	print(track.artist)
	print(track.title)
	path_pcm = create_pcm(track.path)

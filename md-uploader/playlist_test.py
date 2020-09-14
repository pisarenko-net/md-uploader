from playlist import Playlist


PATH_MUSIC = '/mnt/music'
SUPPORTED_EXTENSIONS = ['flac']

playlist = Playlist(PATH_MUSIC, SUPPORTED_EXTENSIONS, '/mnt/music/_minidisc_queue/test.m3u8')

print(playlist.count())
print(playlist.title())
print(playlist.duration())
print(playlist.is_single_artist())

for track in playlist:
	print(track.path)

from transliterate import translit
import usb1

from netmd import netmd_device as devices
from netmd.download import download_track, download_bulk_context_manager
from playlist import archive_playlist, find_next_playlist_path_name, Playlist
from transcode import create_pcm


PATH_MUSIC = '/mnt/music'
SUPPORTED_EXTENSIONS = ['flac']
PLAYLIST_QUEUE_PATH = '/mnt/music/_minidisc_queue'
PLAYLIST_ARCHIVE_PATH = '/mnt/music/_minidisc_queue/archive'
TRANSLITERATION_LANGUAGE = 'ru'

strip_ascii = lambda string: string.encode('ascii', errors='ignore').decode('ascii')
clean_string = lambda string: strip_ascii(translit(string, TRANSLITERATION_LANGUAGE, reversed=True))

playlist_path_name = find_next_playlist_path_name(PLAYLIST_QUEUE_PATH)
if not playlist_path_name:
    print('Playlist queue in %s is empty' % PLAYLIST_QUEUE_PATH)
    exit(0)

playlist = Playlist(PATH_MUSIC, SUPPORTED_EXTENSIONS, playlist_path_name)

try:
    net_md = next(devices)
except StopIteration:
    print('No NetMD devices found')
    exit(1)
except usb1.USBErrorAccess:
    print("Your user doesn't have sufficient access. Either try with root or better construct a udev rule.")
    exit(1)

print(playlist.duration())

is_va_disc = not playlist.is_single_artist()
md_disc_title = playlist.title()

net_md.erase_disc()
net_md.set_disc_title(clean_string(md_disc_title))

with download_bulk_context_manager(net_md) as session:
    for track in playlist:
        md_track_title = clean_string(track.title if not is_va_disc else '%s - %s' % (track.artist, track.title))
        path_pcm = create_pcm(track.path)
        print(md_track_title)

        (track_number, uuid, ccid) = session.download_next(path_pcm, md_track_title)
        print('Track:', track_number)
        print("UUID:",''.join(["%02x" % ord(i) for i in uuid]))
        print("Confirmed Content ID:",''.join(["%02x"%ord(i) for i in ccid]))

archive_playlist(playlist_path_name, PLAYLIST_ARCHIVE_PATH)

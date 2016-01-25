import requests
import time
import os
import argparse
from requests_toolbelt.multipart.encoder import MultipartEncoderMonitor
from tqdm import tqdm

poll_interval = 1
cache = {}


def progress(bytes_read, pbar):
    chunk_len = bytes_read - progress.last_len
    pbar.update(chunk_len)
    progress.last_len = bytes_read


def send_file(name, size):
    encoder = MultipartEncoderMonitor.from_fields(
        fields={'file': (name, open(os.path.join(args.directory_path, name), 'rb'))}
    )
    progress.last_len = 0
    pbar = tqdm(total=encoder.len, leave=True, unit_scale=True, unit='B', miniters=1, desc='sending {}'.format(name))
    monitor = MultipartEncoderMonitor(encoder, lambda monitor: progress(monitor.bytes_read, pbar))

    r = requests.post(upload_url, data=monitor, headers={'Content-Type': monitor.content_type})
    progress(size, pbar)
    if 'Success' not in r.text:
        print(r.text)
    else:
        print('done.\a')


def remove_file(name):
    print('removing {}'.format(name))
    delete_url = '{}?DEL={}'.format(upload_url, name)
    r = requests.get(delete_url)
    if 'SUCCESS' not in r.text:
        print(r.text)
    else:
        print('done.\a')


def check_dir():
    first_run = len(cache) == 0
    files = []
    for name in os.listdir(args.directory_path):
        file_path = os.path.join(args.directory_path, name)
        if os.path.isfile(file_path) and name.endswith('.{}'.format(args.file_extension)):
            files.append(name)
            stat = os.stat(file_path)
            if name not in cache or cache[name] != stat.st_mtime:
                cache[name] = stat.st_mtime
                if not first_run:
                    send_file(name, stat.st_size)

    for name in list(cache.keys()):
        if name not in files:
            remove_file(name)
            del cache[name]


parser = argparse.ArgumentParser(description='Watch a directory for change/delete events to files and sync to flashair card (not recursive!).')
parser.add_argument('directory_path', help='the directory to watch for changes on .x3g files.')
parser.add_argument('flashair_address', help='the address of your flashair card, eg. "192.168.178.41"')
parser.add_argument('file_extension', nargs='?', default='x3g')
args = parser.parse_args()

url = 'http://{}'.format(args.flashair_address)
upload_url = '{}/upload.cgi'.format(url)

while True:
    check_dir()
    time.sleep(poll_interval)

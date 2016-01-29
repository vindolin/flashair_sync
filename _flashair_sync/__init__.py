#!/usr/bin/env python
import requests
import time
import os
import argparse
from requests_toolbelt.multipart.encoder import MultipartEncoderMonitor
from tqdm import tqdm
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

cache = {}


def progress(bytes_read, pbar):
    chunk_len = bytes_read - progress.last_len
    pbar.update(chunk_len)
    progress.last_len = bytes_read


def send_file(name, size):
    try:
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

    except UnicodeDecodeError:
        exit('Oops, unicode filenames are not yet supported, please delete the file "{}" and try again. :('.format(name))


def get_remote_list():
    result = {}
    r = requests.get('{}/command.cgi?op=100&DIR=/'.format(url))
    for line in list(r.text.strip().split('\r\n'))[1:]:
        parts = line.split(',')
        name = parts[1]
        size = int(parts[2])
        attr = int(parts[3])

        if not attr & 16:  # not a directory
            result[name] = size

    return result


def remove_file(name):
    print('removing {}'.format(name))
    delete_url = '{}?DEL={}'.format(upload_url, quote(name))
    r = requests.get(delete_url)
    if 'SUCCESS' not in r.text:
        print(r.text)
    else:
        print('done.\a')


def check_dir():
    if not hasattr(check_dir, 'first_run'):
        check_dir.first_run = True

    files = []
    for name in os.listdir(args.directory_path):
        file_path = os.path.join(args.directory_path, name)

        if os.path.isfile(file_path):
            extension = os.path.splitext(file_path)[1]

            if len(args.file_extensions) == 0 or extension in args.file_extensions:
                files.append(name)
                stat = os.stat(file_path)

                if check_dir.first_run:
                    if args.initial_sync:
                        # file is not on card or has different size
                        if name not in initial_remote_list or initial_remote_list[name] != stat.st_size:
                            send_file(name, stat.st_size)

                    cache[name] = stat.st_mtime

                else:
                    # file is new or has changed
                    if name not in cache or cache[name] != stat.st_mtime:
                        send_file(name, stat.st_size)
                        cache[name] = stat.st_mtime

    # check for deleted files
    for name in list(cache.keys()):
        if name not in files:
            remove_file(name)
            del cache[name]

    # check for remote files that are not in the current directory and delete them
    if check_dir.first_run and args.initial_sync:
        for name, size in initial_remote_list.items():
            if name not in cache:
                remove_file(name)

    check_dir.first_run = False


parser = argparse.ArgumentParser(description='Watch a directory for change/delete events to files and sync to flashair card (not recursive!).')
parser.add_argument('directory_path', help='The directory to watch for changes.')
parser.add_argument('flashair_address', help='The address of your flashair card, eg. "192.168.178.41"')
parser.add_argument('file_extensions', nargs='*', default=None, help='Only files that match one of these extensions get monitored.')
parser.add_argument('-p', '--poll_interval', type=float, default=1, help='How many seconds between directory polls (default is 1).')
parser.add_argument('-i', '--initial_sync', action='store_true', default=False, help='Copy all files that are new or changed to the card on program start, also delete all files on the card which are not in the current directory. Without this switch only files that are new/modified/deleted after the program start are synced.')
args = parser.parse_args()

args.file_extensions = ['.{}'.format(extension) for extension in args.file_extensions]

url = 'http://{}'.format(args.flashair_address)
upload_url = '{}/upload.cgi'.format(url)

if args.initial_sync:
    initial_remote_list = get_remote_list()

while True:
    check_dir()
    time.sleep(args.poll_interval)

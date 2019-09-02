import youtube_dl
import sys
import re
import requests

from options import download_opts, info_opts, file_format
from parse import args


def my_hook(d):
    if d['status'] == 'finished':
        print(d['filename'])


class Logger:
    def __init__(self):
        print("Logger created")
        self.result = None
        self.filename = None

    def debug(self, msg):
        print(msg)
        self.result = msg

        if msg.startswith('[download] '):  # The message contains info about destination
            print("FOUND")
            fpattern = r"storage\/.+?(?=\.)"  # Needs to be saved(and fixed in the future)
            fname = re.search(fpattern, msg)  # TODO: Add custom storage dir

            self.filename = fname.group()

    def warning(self, msg):
        print("Warning:", msg)
        self.result = msg

    def error(self, msg):
        print("Error:", msg)
        self.result = msg


class Downloader:
    def __init__(self):
        print("Downloader created")
        self.logger = Logger()
        download_opts.update({"logger": self.logger})
        info_opts.update({"logger": self.logger})

    def download(self, link, audio_format="mp3"):
        file_format.update({'preferredcodec': audio_format})
        download_opts['postprocessors'].append(file_format)
        download_opts['progress_hooks'].append(my_hook)
        print(download_opts)

        try:
            with youtube_dl.YoutubeDL(download_opts) as ydl:
                ydl.download([link])  # Wait here for response(OK = 0)
                # Filename is known by the time this function ends
        except:
            e = sys.exc_info()[0]
            print("Except error:", e)
            print(self.logger.result)

        return self.logger.filename

    def info(self, link):
        try:
            with youtube_dl.YoutubeDL(info_opts) as ydl:
                ydl.download([link])
        except:
            pass

        print(self.logger.result)


def main():
    print(args.format)
    loader = Downloader()
    if args.info:
        loader.info(args.link[0])
    elif args.format:
        loader.download(args.link[0], args.format[0])


if __name__ == "__main__":
    main()

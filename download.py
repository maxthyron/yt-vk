import youtube_dl
import sys
import re
import zipfile
import os

from options import download_opts, info_opts, file_format
from parse import args


class Logger:
    def __init__(self):
        print("Logger created")
        self.result = None
        self.filename = None

    def debug(self, msg):
        print(msg)
        self.result = msg

        if msg.startswith('[ffmpeg] Destination:'):  # The message contains info about destination
            fpattern = r"/.*\.(wav|webm|mp3|m4a)"  # Needs to be saved(and
            # fixed in
            # the
            # future)
            fname = re.search(fpattern, msg)  # TODO: Add custom storage dir

            self.filename = fname.group()

    def warning(self, msg):
        print("Warning:", msg)
        self.result = msg

    def error(self, msg):
        print("Error:", msg)
        self.result = msg


class Downloader:
    def __init__(self, storage_path="storage"):
        print("Downloader created")
        self.storage_path = storage_path
        self.logger = Logger()
        download_opts.update(
            {"logger":  self.logger,
             "outtmpl": storage_path + '/%(title)s---%(uploader)s.%(ext)s',
             })
        info_opts.update({"logger": self.logger})

    def download(self, link, audio_format="mp3", zip_file=False):
        file_format.update({'preferredcodec': audio_format})
        download_opts['postprocessors'].append(file_format)

        try:
            with youtube_dl.YoutubeDL(download_opts) as ydl:
                ydl.download([link])  # Wait here for response(OK = 0)
                # Filename is known by the time this function ends
        except Exception as e:
            print(e)
            print(self.logger.result)

        file_path = self.storage_path + self.logger.filename
        if zip_file:
            print()
            self.zip(file_path)
        return file_path

    def zip(self, path):
        with zipfile.ZipFile(path + ".wav", 'w', zipfile.ZIP_STORED) as ziph:
            ziph.write(path)

    def info(self, link):
        try:
            with youtube_dl.YoutubeDL(info_opts) as ydl:
                ydl.download([link])
        except:
            pass

        print(self.logger.result)


def main():
    loader = Downloader()
    if args.info:
        loader.info(args.link[0])
    elif args.format:
        loader.download(args.link[0], args.format[0], zip_file=True)


if __name__ == "__main__":
    main()

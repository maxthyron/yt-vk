import youtube_dl
import sys
import re


def get_filename(msg):
    fpattern = r"storage\/.*\.(wav|mp3|m4a)"
    fnames = re.finditer(fpattern, msg)

    result = []
    for name in fnames:
        result.append([name.group()] + name.group().strip("storage/.mp3").split("---"))
    return result


class Intercepter():
    def __init__(self):
        self.result = None
        self.type = None

    def debug(self, msg):
        if msg.startswith('[ffmpeg] Destination:'):
            self.result = msg
        else:
            print(msg)
            self.type = 'other'

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


download_opts = {
    'format':         'bestaudio/best',
    'postprocessors': [{
        'key':              'FFmpegExtractAudio',
        'preferredcodec':   'm4a',
        'preferredquality': '320',
        }],
    'outtmpl':        'storage/%(title)s---%(uploader)s.%(ext)s',
    'logger':         None,
    }

info_opts = {
    'listformats': True,
    'logger':      None,
    }


def get_audio(link):
    inter = Intercepter()
    download_opts['logger'] = inter
    try:
        with youtube_dl.YoutubeDL(download_opts) as ydl:
            ydl.download([link])
    except:
        pass
    return get_filename(inter.result)


def get_info(link):
    inter = Intercepter()
    info_opts['logger'] = inter
    try:
        with youtube_dl.YoutubeDL(info_opts) as ydl:
            ydl.download([link])
        print(inter.result if inter.result or inter.type == 'other' else "Fail")
    except:
        pass


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'get':
            get_audio(link)
        elif sys.argv[1] == 'info':
            get_info(link)


if __name__ == "__main__":
    main()

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

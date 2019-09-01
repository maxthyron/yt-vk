download_opts = {
    'format':         'bestaudio/best',
    'postprocessors': [],
    'outtmpl':        'storage/%(title)s---%(uploader)s.%(ext)s',
    }

file_format = {
    'key':              'FFmpegExtractAudio',
    'preferredquality': '320',
    }

info_opts = {
    'listformats': True,
    }

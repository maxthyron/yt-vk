download_opts = {
    'format':         'bestaudio/best',
    'postprocessors': [],
    'outtmpl':        'storage/%(title)s---%(uploader)s.%(ext)s',
    'progress_hooks': [],
    }

file_format = {
    'key':              'FFmpegExtractAudio',
    'preferredquality': '320',
    }

info_opts = {
    'listformats':    True,
    'progress_hooks': [],
    }

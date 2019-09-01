import argparse

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

parser.add_argument("-l", "--link", dest="link", action="store",
                    nargs=1, help="Youtube link to get info/audio")

group.add_argument("-i", "--info", dest="info", action="store_true",
                   help="Flag to get info about the video")

group.add_argument("-f", "--format", default="mp3", dest="format", action="store",
                   nargs=1, help="Download format for the audio")

args = parser.parse_args()

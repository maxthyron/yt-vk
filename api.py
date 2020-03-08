import os
import vk_api
import re
import dotenv
import requests
import time
import socket
import urllib3
import signal
import sys
import pprint

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from download import Downloader

TIMEOUT_SECONDS = 10

class VkBot:
    def __init__(self):
        self.timeout = TIMEOUT_SECONDS
        signal.signal(signal.SIGTERM, self.catch_signal)
        self.init_connection()

    def init_connection(self):
        try:
            self.vk_session = vk_api.VkApi(login=os.getenv("LOGIN"), password=os.getenv("PASSW"))
            try:
                self.vk_session.auth(token_only=True)
            except vk_api.AuthError as e:
                print(e)
                sys.exit(0)
            except vk_api.exceptions.Captcha as e:
                print("CAPTCHA")
                print(e.get_url())
                code = input()
                e.try_again(key=code)

            print("ID:", os.getpid())
            print("Got VK API Session")
            self.group_session = vk_api.VkApi(token=os.getenv("KEY"))
            print("Got Group Session")
            self.longpoll = VkBotLongPoll(self.group_session, os.getenv("GROUP_ID"))
            print("Got Longpoll Object")
            self.api = self.vk_session.get_api()
            print("Got API Object")
            self.group_api = self.group_session.get_api()
            print("Got Group API Object")
            self.upload = vk_api.VkUpload(self.vk_session)
            print("Got Upload Object")
            self.loader = Downloader()
            print("Got Downloader Object")
        except (requests.exceptions.ConnectionError) as e:
            print("Reinitializing session data")
            print(e)
            print("Timeout:", self.timeout)
            time.sleep(self.timeout)
            self.timeout += 1
            self.init_connection()

    def catch_signal(self, signal, frame):
        print("Stopping...")
        sys.exit(0)

    def send_message(self, user_id, message, attachment=None):
        self.group_api.messages.send(user_id=user_id,
                                     random_id=get_random_id(),
                                     message=message,
                                     attachment=attachment)

    def response(self, event):
        self.send_message(user_id=event.obj.message["from_id"], message="Wait a bit")
        link = self.find_yt(event.obj)
        if link:
            result = self.loader.download(link)
            if result:
                if not result.endswith(".mp3"):
                    index = result.find(".")
                    path = result.replace(result[index:], ".mp3")
                else:
                    path = result
                title, artist = result.lstrip("storage/").rstrip(".mp3").split("---")
                self.upload_yt(event, path, title, artist)
                os.remove(path)
        else:
            self.send_error(event)
        print()

    def start(self):
        print("Start Longpoll listening")
        while True:
            try:
                for event in self.longpoll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        print("Event:\n", pprint.pprint(event.obj))
                        print("From:", event.obj.message["from_id"])
                        print('Message:', event.obj.message["text"])
                        self.response(event)
                    elif event.type == VkBotEventType.MESSAGE_REPLY:
                        print("From(Bot):", event.obj.peer_id)
                        print('Message(Bot):', event.obj.text)
                        print()
                    else:
                        print(event.type)
                        print()
            except (requests.exceptions.ReadTimeout) as e:
                print("Got exception")
                print(type(e))
                print(e)
                time.sleep(self.timeout)
                self.init_connection()
                self.timeout = TIMEOUT_SECONDS
                self.start()

    def upload_yt(self, event, path, title, artist):
        try:
            audio = self.upload.audio(audio=path, title=title, artist=artist)
        except vk_api.exceptions.ApiError as e:
            self.send_message(user_id=event.obj.message["from_id"], message=f"{e.error['error_msg']}")
        else:
            self.send_message(user_id=event.obj.message["from_id"], message="Your audio:",
                              attachment=f"audio{audio['owner_id']}_{audio['id']}")

    def send_error(self, event):
        self.send_message(user_id=event.obj.message["from_id"], message='',
                          attachment='photo-185940778_457239022')

    def find_yt(self, event):
        if event.message["text"] != '':
            pattern = r'(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.\S*'
            result = re.search(pattern, event.message["text"])
            if result:
                return result.group()
        else:
            if event.message['attachments']:
                attachment = event.message['attachments'][0]
            else:
                return

            if attachment['type'] != 'video' or attachment['video'].get('platform') != 'YouTube':
                return

            videos = self.api.video.get(
                videos=f"{attachment['video']['owner_id']}_{attachment['video']['id']}"
                )

            if not videos['items']:
                return

            return videos['items'][0]['player']


def upload_doc(vk, upload, event, path, title):
    doc = upload.document(path, title=title, tags=[], message_peer_id=event.obj.peer_id)['doc']
    print(doc)
    vk.messages.send(user_id=event.obj.message["from_id"], random_id=get_random_id(),
                     attachment=f"doc{doc['owner_id']}_{doc['id']}")


if __name__ == '__main__':
    dotenv_file = dotenv.load_dotenv(verbose=True)
    bot = VkBot()
    bot.start()

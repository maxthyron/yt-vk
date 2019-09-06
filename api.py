import vk_api
import re
import os

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from env import auth
from download import Downloader


class VkBot:
    def __init__(self):
        self.vk_session = vk_api.VkApi(login=auth.LOGIN, password=auth.PASSW)
        try:
            self.vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            print(error_msg)
            return

        print("Got VK API Session")
        self.group_session = vk_api.VkApi(token=auth.KEY)
        print("Got Group Session")
        self.longpoll = VkBotLongPoll(self.group_session, auth.GROUP_ID)
        print("Got Longpoll Object")
        self.api = self.vk_session.get_api()
        print("Got API Object")
        self.group_api = self.group_session.get_api()
        print("Got Group API Object")
        self.upload = vk_api.VkUpload(self.vk_session)
        print("Got Upload Object")
        self.loader = Downloader()
        print("Got Downloader Object")

    def send_message(self, user_id, message, attachment=None):
        self.group_api.messages.send(user_id=user_id,
                                     random_id=get_random_id(),
                                     message=message,
                                     attachment=attachment)

    def response(self, event):
        self.send_message(user_id=event.obj.from_id, message="Wait a bit")
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
                        print("From:", event.obj.from_id)
                        print('Message:', event.obj.text)
                        if event.obj.from_id == 50478658:
                            self.send_message(event.obj.from_id, 'Privet, My Kucold Highness!')
                        self.response(event)
                    elif event.type == VkBotEventType.MESSAGE_REPLY:
                        print("From(Bot):", event.obj.peer_id)
                        print('Message:', event.obj.text)
                        print()
                    else:
                        print(event.type)
                        print()
            except Exception:
                self.start()

    def upload_yt(self, event, path, title, artist):
        try:
            audio = self.upload.audio(audio=path, title=title, artist=artist)
        except vk_api.exceptions.ApiError as e:
            self.send_message(user_id=event.obj.from_id, message=f"{e.error['error_msg']}")
        else:
            self.send_message(user_id=event.obj.from_id, message="Your audio:",
                              attachment=f"audio{audio['owner_id']}_{audio['id']}")

    def send_error(self, event):
        self.send_message(user_id=event.obj.from_id, message='',
                          attachment='photo-185940778_457239022')

    def find_yt(self, event):
        if event.text != '':
            pattern = r'(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.\S*'
            result = re.search(pattern, event.text)
            if result:
                return result.group()
        else:
            if event['attachments']:
                attachment = event['attachments'][0]
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
    vk.messages.send(user_id=event.obj.from_id, random_id=get_random_id(),
                     attachment=f"doc{doc['owner_id']}_{doc['id']}")


if __name__ == '__main__':
    bot = VkBot()
    bot.start()

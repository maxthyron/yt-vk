import vk_api
import json
import re
import time

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from env import auth
from download import Downloader


class VkBot:
    def __init__(self):
        self.vk_session = vk_api.VkApi(login=auth.LOGIN, password=auth.PASSW, token=auth.KEY)
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

    def start(self):
        print("Start Longpoll listening")
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                print("From:", event.obj.from_id)
                print('Message:', event.obj.text)
                self.group_api.messages.send(user_id=event.obj.from_id,
                                             random_id=get_random_id(),
                                             message="Wait a bit")
                link = self.find_yt(event.obj)
                if link:
                    result = self.loader.download(link)
                    print(result)
                    if result:
                        path = result + ".mp3"  # TODO: Change this
                        title, artist = result.strip("storage/").split("---")
                        # TODO: Bug - Ayase -> Ay
                        self.upload_yt(event, path, title, artist)

                else:
                    self.group_api.messages.send(user_id=event.obj.from_id,
                                                 random_id=get_random_id(),
                                                 message="Video not found")

            elif event.type == VkBotEventType.MESSAGE_REPLY:
                print("From(Bot):", event.obj.peer_id)
                print('Message:', event.obj.text)
                print()
            else:
                print(event.type)
                print()

    def upload_yt(self, event, path, title, artist):
        try:
            audio = self.upload.audio(audio=path,
                                      artist=artist,
                                      title=title)
        except vk_api.exceptions.ApiError as e:
            self.group_api.messages.send(user_id=event.obj.from_id,
                                         random_id=get_random_id(),
                                         message=f"{e.error['error_msg']}")
        else:
            self.group_api.messages.send(user_id=event.obj.from_id,
                                         random_id=get_random_id(),
                                         message="Your audio:",
                                         attachment=f"audio{audio['owner_id']}_{audio['id']}")

    def find_yt(self, event):
        if event.text != '':
            pattern = r'(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.\S*'
            return re.search(pattern, event.text).group()
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

            if len(videos['items']) == 0:
                return

            return videos['items'][0]['player']


def upload_doc(vk, upload, event, path, title):
    doc = upload.document(path, title=title, tags=[], message_peer_id=event.obj.peer_id)['doc']
    print(doc)
    vk.messages.send(user_id=event.obj.from_id, random_id=get_random_id(),
                     attachment=f"doc{doc['owner_id']}_{doc['id']}")


def main():
    bot = VkBot()
    bot.start()


if __name__ == '__main__':
    main()

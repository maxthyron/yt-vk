import vk_api
import json
import re

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from env import auth
from download import Downloader


def find_yt(api, event):
    links = None
    if event.text != '':
        pattern = r'(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.\S*'
        links = [l.group() for l in re.finditer(pattern, event.text)]
    else:
        print(event['attachments'])
        owner_id = event['attachments'][0]['video']['owner_id']
        att_id = event['attachments'][0]['video']['id']
        print(api.video.get(owner_id=owner_id,
                            videos=f"{owner_id}_{att_id}")['items'][0]['player'])
        links = [api.video.get(owner_id=owner_id,
                               videos=f"{owner_id}_{att_id}")['items'][0]['player']]

    return links


def upload_doc(vk, upload, event, path, title):
    doc = upload.document(path, title=title, tags=[], message_peer_id=event.obj.peer_id)['doc']
    print(doc)
    vk.messages.send(user_id=event.obj.from_id, random_id=get_random_id(),
                     attachment=f"doc{doc['owner_id']}_{doc['id']}")


def upload_yt(vk, upload, event, path, title, artist):
    audio = upload.audio(audio=path,
                         artist=artist,
                         title=title)
    vk.messages.send(user_id=event.obj.from_id,
                     random_id=get_random_id(),
                     attachment=f"audio{audio['owner_id']}_{audio['id']}")


def main():
    vk_session = vk_api.VkApi(token=auth.KEY)
    print("Got VK API Session")
    longpoll = VkBotLongPoll(vk_session, auth.GROUP_ID)
    print("Got Group Session")
    vk = vk_session.get_api()
    print("Got VK API Object")

    audio_session = vk_api.VkApi(login=auth.LOGIN, password=auth.PASSW)
    try:
        audio_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    print("Got Audio Session")
    new_vk = audio_session.get_api()
    upload = vk_api.VkUpload(audio_session)
    print("Got Upload Object")
    loader = Downloader()
    audio_format = "mp3"
    print("Start Longpoll listening")
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            print("From:", event.obj.from_id)
            print("Content:", event.obj['attachments'])
            print('Message:', event.obj.text)
            links = find_yt(new_vk, event.obj)
            if links:
                for l in links:
                    result = loader.download(l)
                    print(result)
                    if result:
                        path = result + f".{audio_format}"
                        title, artist = result.strip("storage/.mp3").split("---")
                        # TODO: Bug - Ayase -> Ay
                        upload_yt(vk, upload, event, path, title, artist)
                        print("BEFORE")
                        # upload_doc(vk, uploadd, event, path, title)
                        print("AFTER")
            else:
                vk.messages.send(user_id=event.obj.from_id,
                                 random_id=get_random_id(),
                                 message="Video not found")

        elif event.type == VkBotEventType.MESSAGE_REPLY:
            print("From(Me):", event.obj.peer_id)
            print('Message:', event.obj.text)
            print()
        else:
            print(event.type)
            print()


if __name__ == '__main__':
    main()

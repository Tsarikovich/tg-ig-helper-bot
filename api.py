from instagrapi import Client
from instagrapi.types import Usertag, UserShort, Location

import config
from helping_functions import log_info, download_and_save_file, clear_directory
import random
import os


class InstagramHandler:
    def __init__(self):
        self.__cl = Client()
        self.__cl.login(os.environ.get('LOGIN', None), os.environ.get('PASSWORD', None))

    def process_url(self, url, caption):
        log_info("Processing url")
        pk = self.__cl.media_pk_from_url(url)
        medias = self.__cl.media_info(pk).dict()

        user = medias['user']
        resources = medias['resources']
        location = medias['location']

        paths = []
        if len(resources) == 0:
            type_post = medias['media_type']
            paths.append(download_and_save_file(medias))
        else:
            type_post = 8
            for index, resource in enumerate(resources):
                paths.append(download_and_save_file(resource, index))

        self.__create_post(user, type_post, paths, caption, location)
        clear_directory()

    def __create_post(self, user, type_post, paths, caption, location):
        log_info("Uploading post")

        user_short = UserShort(pk=user['pk'], username=user['username'])
        user_tag = [
            Usertag(user=user_short, x=round(random.uniform(0.2, 0.8), 2), y=round(random.uniform(0.2, 0.8), 2))]

        caption = caption.format(user['username'])

        if location is not None:
            location = Location(pk=location['pk'], name=location['name'], external_id=location['external_id'])
        else:
            location = Location(name="Moscow, Russia")

        media = None
        if type_post == 1:
            media = self.__cl.photo_upload(paths[0], caption=caption, usertags=user_tag, location=location)

        if type_post == 2:
            media = self.__cl.video_upload(paths[0], caption=caption, usertags=user_tag, location=location)

        if type_post == 8:
            media = self.__cl.album_upload(paths, caption=caption, usertags=user_tag, location=location)

        self.__add_comment(media)

        log_info("Success!")

    def __add_comment(self, media):
        if media is not None:
            self.__cl.media_comment(media.dict()['id'], config.HASHTAGS)

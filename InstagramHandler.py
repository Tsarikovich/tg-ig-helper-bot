from instagrapi.types import Usertag, UserShort, Location

from helping_functions import *


class InstagramHandler:
    def __init__(self, credentials):
        self.__clients = {}
        self.output = open(config.PathTo.USED_USERS, "a")

        json_cred = json.loads(credentials)

        log_info("Signing into accounts")
        for account in json_cred:
            self.__clients[json_cred[account]['login']] = {"client": Client(), "is_posting": False}
            self.__clients[json_cred[account]['login']]["client"].login(json_cred[account]['login'],
                                                                        json_cred[account]['password'])

            log_info(f"Successfully signed into {json_cred[account]['login']}")

    def process_url(self, account_name, url, caption):
        log_info("Processing url")

        client = self.__clients[account_name]["client"]
        self.__clients[account_name]["is_posting"] = True

        medias = client.media_info(client.media_pk_from_url(url)).dict()
        user, resources, location = medias['user'], medias['resources'], medias['location']

        paths_to_downloaded_res = []
        if len(resources) == 0:
            type_post = medias['media_type']  # photo/video
            paths_to_downloaded_res.append(download_and_save_file(medias))
        else:
            type_post = 8  # album
            for index, resource in enumerate(resources):
                paths_to_downloaded_res.append(download_and_save_file(resource, index))

        self.__create_post(client, user, type_post, paths_to_downloaded_res, caption, location)
        clear_directory()

    def __create_post(self, client, user, type_post, paths, caption, location):
        log_info("Uploading post")

        user_short = UserShort(pk=user['pk'], username=user['username'])
        user_tag = [
            Usertag(user=user_short, x=round(random.uniform(0.2, 0.8), 2), y=round(random.uniform(0.2, 0.8), 2))]

        caption = caption.format(user['username'], client.username)

        if location is not None:
            location = client.location_complete(
                Location(pk=location['pk'], name=location['name'], address=location['address']))
        else:
            location = client.location_complete(Location(pk=213326726, name="Warsaw, Poland", address="Warsaw, Poland"))

        media = None
        if type_post == 1:
            media = client.photo_upload(paths[0], caption=caption, usertags=user_tag, location=location)

        if type_post == 2:
            media = client.video_upload(paths[0], caption=caption, usertags=user_tag, location=location)

        if type_post == 8:
            media = client.album_upload(paths, caption=caption, usertags=user_tag, location=location)

        self.__comment_hashtags(client, media)
        self.__like_and_comment_each_other(media, client.username)

        self.__clients[client.username]["is_posting"] = False
        log_info("Success!")

    def __comment_hashtags(self, client, media):
        log_info("Commenting hashtags")
        client.media_comment(media.dict()['id'], config.HASHTAGS)

    def __like_and_comment_each_other(self, media, current_account):
        log_info("Liking and commenting each other")

        for client_name in self.__clients:
            if client_name != current_account:
                curr_client = self.__clients[client_name]["client"]
                curr_client.media_like(media.id)
                curr_client.media_comment(media.id, random.choice(config.COMMENTS_TEMPLATES))

    def public_activity(self):
        schedules = {}
        scrapped_users = {}

        for client in self.__clients:
            schedules[client] = calculate_schedule_activity()
            scrapped_users[client] = scrape_users(client)

        dates_list_not_empty = True

        while dates_list_not_empty:
            for account in schedules:
                if self.__clients[account]["is_posting"]:
                    continue

                newest_date_follow, newest_date_like, newest_date_comment = None, None, None

                if len(schedules[account]['follow']) > 0:
                    newest_date_follow = schedules[account]['follow'][0]
                if len(schedules[account]['like']) > 0:
                    newest_date_like = schedules[account]['like'][0]
                if len(schedules[account]['comment']) > 0:
                    newest_date_comment = schedules[account]['comment'][0]

                if not newest_date_follow and not newest_date_like and not newest_date_comment:
                    dates_list_not_empty = False
                    break

                if newest_date_follow and datetime.datetime.now() > newest_date_follow:
                    user_id = scrapped_users[account].pop()
                    self.__clients[account]["client"].user_follow(user_id)
                    self.output.write(user_id + "\n")
                    heapq.heappop(schedules[account]['follow'])

                if newest_date_like and datetime.datetime.now() > newest_date_like:
                    user_id = scrapped_users[account].pop()

                    user_media = self.__clients[account]["client"].user_medias(user_id=int(user_id), amount=3)
                    for media in user_media:
                        self.__clients[account]["client"].media_like(media.id)

                    self.output.write(user_id + "\n")
                    heapq.heappop(schedules[account]['like'])

                if newest_date_comment and datetime.datetime.now() > newest_date_comment:
                    user_id = scrapped_users[account].pop()

                    user_media = self.__clients[account]["client"].user_medias(user_id=int(user_id), amount=1)
                    self.__clients[account]["client"].media_comment(user_media[0].id,
                                                                    text=random.choice(config.COMMENTS_TEMPLATES))
                    self.output.write(user_id + "\n")
                    heapq.heappop(schedules[account]['comment'])

            time.sleep(60)

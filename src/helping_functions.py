import datetime
import heapq
import json
import os
import random
import shutil
import time
from pathlib import Path

import config
import ig_bot_settings
import requests
from config import logger
from instagrapi import Client
from instagrapi.types import UserShort, Usertag
from selenium import webdriver


def download_and_save_file(resource, index=0):
    logger.debug('Downloading files')
    resource_type = resource['media_type']

    if resource_type == 1:
        resource_type = '.jpg'
        file_url = resource['thumbnail_url']
    else:
        resource_type = '.mp4'
        file_url = resource['video_url']

    response = requests.get(file_url)

    path = f'{config.PathTo.DOWNLOAD}temp{index}{resource_type}'
    with open(path, 'wb') as file:
        file.write(response.content)

    return Path(path)


def clear_directory():
    for filename in os.listdir(config.PathTo.DOWNLOAD):
        filepath = os.path.join(config.PathTo.DOWNLOAD, filename)
        try:
            shutil.rmtree(filepath)
        except OSError:
            os.remove(filepath)


def get_account_names():
    accounts_json = json.loads('../credentials.json')
    return [accounts_json[account]['login'] for account in accounts_json]


def calculate_schedule_activity():
    logger.debug('Calculating schedule activity')

    today_follows_amount = random.randint(
        ig_bot_settings.ACCOUNTS_TO_FOLLOW_PER_DAY[0],
        ig_bot_settings.ACCOUNTS_TO_FOLLOW_PER_DAY[1],
    )
    today_likes_amount = random.randint(
        ig_bot_settings.ACCOUNTS_TO_LIKE_PER_DAY[0],
        ig_bot_settings.ACCOUNTS_TO_LIKE_PER_DAY[1],
    )
    today_comments_amount = random.randint(
        ig_bot_settings.ACCOUNTS_TO_COMMENT_PER_DAY[0],
        ig_bot_settings.ACCOUNTS_TO_COMMENT_PER_DAY[1],
    )

    start_date = datetime.datetime.today()
    follow_time, likes_time, comments_time = [], [], []

    for i in range(today_follows_amount):
        follow_time.append(
            start_date
            + datetime.timedelta(
                seconds=random.randrange(
                    60 * 60 * ig_bot_settings.HOURS_TO_WORK
                )
            )
        )

    for i in range(today_likes_amount):
        likes_time.append(
            start_date
            + datetime.timedelta(
                seconds=random.randrange(
                    60 * 60 * ig_bot_settings.HOURS_TO_WORK
                )
            )
        )

    for i in range(today_comments_amount):
        comments_time.append(
            start_date
            + datetime.timedelta(
                seconds=random.randrange(
                    60 * 60 * ig_bot_settings.HOURS_TO_WORK
                )
            )
        )

    return {
        'follow': heapq.heapify(follow_time),
        'like': heapq.heapify(likes_time),
        'comment': heapq.heapify(comments_time),
    }


def load_data():
    used_users = set()

    with open(config.PathTo.USED_USERS) as file:
        data = file.read().split()
        [used_users.add(user_id) for user_id in data]

    people_ids = []
    with open(config.PathTo.SOURCE_TRAFFIC_PEOPLE) as file:
        data = file.read().split()
        [people_ids.append(people_data.split(',')[1]) for people_data in data]

    group_ids = []
    with open(config.PathTo.SOURCE_TRAFFIC_GROUPS) as file:
        data = file.read().split()
        [group_ids.append(group_data.split(',')[1]) for group_data in data]

    return used_users, people_ids, group_ids


def scrape_by_source(client, ids, used_users, scrapped_users, source=1):
    logger.debug(f"Scrapping from {'groups' if source else 'people'}")
    random.shuffle(ids)

    ids = ids[
        : ig_bot_settings.GROUPS_TO_CHECK
        if source
        else ig_bot_settings.PEOPLE_TO_CHECK
    ]

    for i, group_id in enumerate(ids):
        logger.debug(f"{i + 1} {'group' if source else 'people'} scrapping")

        followers = client.user_followers(
            user_id=group_id,
            amount=(
                ig_bot_settings.NUM_TO_REQUEST_PER_CATEGORY_GROUPS
                if source
                else ig_bot_settings.NUM_TO_REQUEST_PER_CATEGORY_PEOPLE
            ),
        )

        for id_ in followers:
            if id_ not in used_users:
                scrapped_users.add((id_, followers[id_].username))

        time.sleep(3)
        # Parse likers of the newest post
        group_media = client.user_medias(user_id=int(group_id), amount=1)
        if len(group_media) > 0:
            likers = client.media_likers(group_media[0].id)
            likers = likers[
                : min(
                    (
                        ig_bot_settings.NUM_TO_REQUEST_PER_CATEGORY_GROUPS
                        if source
                        else ig_bot_settings.NUM_TO_REQUEST_PER_CATEGORY_PEOPLE
                    ),
                    len(likers),
                )
            ]

            for user in likers:
                if user not in used_users:
                    scrapped_users.add((user.pk, user.username))

        time.sleep(3)
        if source:
            # Parse taggers
            medias = client.usertag_medias(user_id=int(group_id), amount=15)
            if len(medias) > 0:
                medias = random.sample(
                    medias,
                    min(
                        ig_bot_settings.NUM_TO_REQUEST_PER_CATEGORY_GROUPS + 5,
                        len(medias),
                    ),
                )
                for media in medias:
                    if media.user.pk not in used_users:
                        scrapped_users.add(
                            (media.user.pk, media.user.username)
                        )

        time.sleep(10)

    return scrapped_users


def scrape_users(client: Client):
    logger.debug('Scrapping')

    used_users, people_ids, group_ids = load_data()
    scrapped_users = set()

    scrapped_users = scrape_by_source(
        client, group_ids, used_users, scrapped_users
    )
    time.sleep(120)
    scrapped_users = scrape_by_source(
        client, people_ids, used_users, scrapped_users, 0
    )

    logger.debug('Scrapping successfully')
    return scrapped_users


def generate_hashtags(hashtags: str):
    logger.debug('Generating hashtags')
    driver = webdriver.Chrome(
        chrome_options=config.HashtagsGen.chrome_options,
    )
    driver.get(config.HashtagsGen.URL)
    driver.find_element_by_xpath(
        '//*[@id="app"]/div/div/div[2]/input'
    ).send_keys(hashtags)
    time.sleep(2)
    driver.find_element_by_xpath(
        '//*[@id="app"]/div/div/div[3]/div[2]/div/button'
    ).click()
    content = driver.find_element_by_xpath('/html/body/div[2]/div').text
    config.HASHTAGS = content
    logger.debug('Successfully generated new hashtags')


def create_usertags(list_ids, amount=5):
    usertags = []
    random.shuffle(list_ids)

    for index, name in enumerate(list_ids[:amount]):
        usershort = UserShort(pk=int(name[1]), username=name[0])
        usertag = Usertag(user=usershort, x=0.83 + index * 0.01, y=0.9)
        usertags.append(usertag)

    return usertags

import shutil
import requests
from pathlib import Path
import config
import time
import os
import json
import random
import datetime
import heapq
from instagrapi import Client
from selenium import webdriver


def log_info(data):
    print(time.strftime("%H:%M:%S", time.localtime()), data)


def download_and_save_file(resource, index=0):
    log_info("Downloading files")
    resource_type = resource['media_type']

    if resource_type == 1:
        resource_type = ".jpg"
        file_url = resource['thumbnail_url']
    else:
        resource_type = ".mp4"
        file_url = resource['video_url']

    response = requests.get(file_url)

    path = f"{config.PathTo.DOWNLOAD}temp{index}{resource_type}"
    open(path, "wb").write(response.content)
    return Path(path)


def clear_directory():
    for filename in os.listdir(config.PathTo.DOWNLOAD):
        filepath = os.path.join(config.PathTo.DOWNLOAD, filename)
        try:
            shutil.rmtree(filepath)
        except OSError:
            os.remove(filepath)


def get_account_names():
    json_accounts = json.loads(os.environ['accounts_list'])
    return [json_accounts[account]["login"] for account in json_accounts]


def calculate_schedule_activity():
    log_info("Calculating schedule activity")

    today_follows_amount = random.randint(config.ACCOUNTS_TO_FOLLOW_PER_DAY[0],
                                          config.ACCOUNTS_TO_FOLLOW_PER_DAY[1])
    today_likes_amount = random.randint(config.ACCOUNTS_TO_LIKE_PER_DAY[0],
                                        config.ACCOUNTS_TO_LIKE_PER_DAY[1])
    today_comments_amount = random.randint(config.ACCOUNTS_TO_COMMENT_PER_DAY[0],
                                           config.ACCOUNTS_TO_COMMENT_PER_DAY[1])

    start_date = datetime.datetime.today()
    follow_time, likes_time, comments_time = [], [], []

    for i in range(today_follows_amount):
        follow_time.append(
            start_date + datetime.timedelta(minutes=random.randrange(60 * config.ScrapeSettings.HOURS_TO_WORK),
                                            seconds=random.randrange(60)))

    for i in range(today_likes_amount):
        likes_time.append(
            start_date + datetime.timedelta(minutes=random.randrange(60 * config.ScrapeSettings.HOURS_TO_WORK),
                                            seconds=random.randrange(60)))

    for i in range(today_comments_amount):
        comments_time.append(
            start_date + datetime.timedelta(minutes=random.randrange(60 * config.ScrapeSettings.HOURS_TO_WORK),
                                            seconds=random.randrange(60)))

    return {"follow": heapq.heapify(follow_time), "like": heapq.heapify(likes_time),
            "comment": heapq.heapify(comments_time)}


def load_data():
    used_users = set()

    with open(config.PathTo.USED_USERS, 'r') as file:
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


def scrape_from_groups(client, group_ids, used_users, scrapped_users):
    log_info("Scrapping from groups")
    random.shuffle(group_ids)
    for i, group_id in enumerate(group_ids[:config.ScrapeSettings.GROUPS_TO_CHECK]):
        log_info(f"{i + 1} group scrapping")
        # Parse followers
        followers = client.user_followers(user_id=group_id,
                                          amount=config.ScrapeSettings.NUM_TO_REQUEST_PER_CATEGORY_GROUPS)
        for id_ in followers:
            if id_ not in used_users:
                scrapped_users.add(id_)

        time.sleep(3)
        # Parse likers of newest post
        group_media = client.user_medias(user_id=int(group_id), amount=1)
        if len(group_media) > 0:
            likers = client.media_likers(group_media[0].id)
            likers = likers[:min(config.ScrapeSettings.NUM_TO_REQUEST_PER_CATEGORY_GROUPS, len(likers))]
            for id_ in likers:
                if id_ not in used_users:
                    scrapped_users.add(id_.pk)

        time.sleep(3)
        # Parse taggers
        medias = client.usertag_medias(user_id=int(group_id), amount=15)
        if len(medias) > 0:
            medias = random.sample(medias,
                                   min(config.ScrapeSettings.NUM_TO_REQUEST_PER_CATEGORY_GROUPS, len(medias)))
            for media in medias:
                if media.user.pk not in used_users:
                    scrapped_users.add(media.user.pk)
        time.sleep(10)

    return scrapped_users


def scrape_from_people(client, people_ids, used_users, scrapped_users):
    log_info("Scrapping from people")
    random.shuffle(people_ids)
    for i, people_id in enumerate(people_ids[:config.ScrapeSettings.PEOPLE_TO_CHECK]):
        log_info(f"{i + 1} people scrapping")
        # Parse followers
        followers = client.user_followers(user_id=people_id,
                                          amount=config.ScrapeSettings.NUM_TO_REQUEST_PER_CATEGORY_PEOPLE)
        for id_ in followers:
            if id_ not in used_users:
                scrapped_users.add(id_)

        time.sleep(3)

        # Parse likers of newest post
        people_media = client.user_medias(user_id=int(people_id), amount=1)
        if len(people_id) > 0:
            likers = client.media_likers(people_media[0].id)
            likers = likers[:min(config.ScrapeSettings.NUM_TO_REQUEST_PER_CATEGORY_PEOPLE, len(likers))]
            for id_ in likers:
                if id_ not in used_users:
                    scrapped_users.add(id_.pk)

        time.sleep(10)
    return scrapped_users


def scrape_users(client: Client):
    log_info("Scrapping")

    used_users, people_ids, group_ids = load_data()
    scrapped_users = set()

    scrapped_users = scrape_from_groups(client, group_ids, used_users, scrapped_users)
    time.sleep(60)
    scrapped_users = scrape_from_people(client, people_ids, used_users, scrapped_users)

    log_info("Scrapping successfully")
    return scrapped_users


def generate_hashtags(hashtags: str):
    log_info("Generating hashtags")

    driver = webdriver.Chrome(executable_path=config.PathTo.CHROME_DRIVER_PATH,
                              chrome_options=config.HashtagsGen.chrome_options)
    driver.get(config.HashtagsGen.URL)
    driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/input').send_keys(hashtags)
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="app"]/div/div/div[3]/div[2]/div/button').click()
    content = driver.find_element_by_xpath("/html/body/div[2]/div").text
    config.HASHTAGS = content
    log_info("Successfully generated new hashtags")

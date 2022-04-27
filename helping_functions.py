import shutil
import requests
from pathlib import Path
import config
import time
import os


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

    path = f"{config.DIR_NAME}temp{index}{resource_type}"
    open(path, "wb").write(response.content)
    return Path(path)


def clear_directory():
    for filename in os.listdir(config.DIR_NAME):
        filepath = os.path.join(config.DIR_NAME, filename)
        try:
            shutil.rmtree(filepath)
        except OSError:
            os.remove(filepath)

# coding:utf-8

import os

USER_INFO_DATA_DIR = "data/userInfo"
ALBUM_DATA_DIR = "data/album"
TAG_DATA_DIR = "data/tag"
TRACK_DATA_DIR = "data/track"
ARTIST_DATA_DIR = "data/artist"
DATA_DIRS = [USER_INFO_DATA_DIR, ALBUM_DATA_DIR, TAG_DATA_DIR, TRACK_DATA_DIR, ARTIST_DATA_DIR]

DOWNDLOADED_USER = "user.txt"
MAX_THREAD_NUM = 40

def make_dirs_and_create_file():
    for dir in DATA_DIRS:
        if not os.path.isdir(dir):
            os.makedirs(dir)
    if not os.path.isfile(DOWNDLOADED_USER):
        open(DOWNDLOADED_USER,"w")
        print("Create user.txt")
    
def init_env():
    make_dirs_and_create_file()

if __name__ == "__main__":
    init_env()

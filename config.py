import os


CLEAN_DOWNLOAD = 1  # this should be one
DOWNLOAD_FOLDER = "download"
DOWNLOAD_PATH = os.path.join(os.getcwd(), DOWNLOAD_FOLDER)

TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
CHAT_ID = -1001234567890
TOPIC_ID = 1

USE_PROXY = 1
PROXY = 'socks5h://127.0.0.1:9050'


def join_path(file):
    return os.path.join(DOWNLOAD_PATH, file)

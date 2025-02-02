import os
import json

from webdriver import WebDriver
from database import Database
from bot import Bot

import config
from codeforces import CodeForces
from quera import Quera
from status import Status

cps_list = [
    CodeForces,
    Quera,
]


def check_folder():
    if os.path.isdir(config.DOWNLOAD_FOLDER):
        return
    os.makedirs(config.DOWNLOAD_FOLDER)


def clean_download():
    for f in os.listdir(config.DOWNLOAD_PATH):
        file = config.join_path(f)

        try:
            os.remove(file)
        except BaseException as e:
            print("Failed to delete", file)
            print(e)


def do():
    file_name, cap = None, None
    if not status.is_in_table(cp.name, diff):
        status.add_cp(cp.name, diff)

    if not status.is_downloaded(cp.name, diff):
        print(cp.name, "dowload", diff)
        file_name, cap = cp.download_with_difficulty(diff)
        print(cp.name, "dowload", diff, "done")
        status.set_download(cp.name, diff)
        status.set_filename(cp.name, diff, file_name)
        p = cp.get_current_problem()
        ps = json.dumps(p).replace('"', '""')
        status.set_problem(cp.name, diff, ps)

    if not status.is_sent(cp.name, diff):
        print(cp.name, "send", diff)
        if file_name is None:
            file_name = status.get_filename(cp.name, diff)
        if cap is None:
            problems = status.get_problem(cp.name, diff)
            problem = json.loads(problems)
            cap = cp.get_caption(problem, diff)
        file_path = config.join_path(file_name)
        bot.send_file(file_path, file_name, cap)
        print(cp.name, "send", diff, "done")
        cp.set_problem_sent()
        status.set_send(cp.name, diff)


if __name__ == "__main__":
    check_folder()
    db = Database()
    driver = WebDriver()
    bot = Bot()
    status = Status(db)

    difficulties = ["easy", "medium", "hard"]
    for i in cps_list:
        cp = i(db=db, webdriver=driver)
        if not db.is_table_exist(cp.name):
            cp.update()

        for diff in difficulties:
            do()

    if config.CLEAN_DOWNLOAD:
        clean_download()
    driver.quit()
    status.clear_table()

import requests
from bs4 import BeautifulSoup

from competitive_programming import CP
import config


class Quera(CP):
    def __init__(self, db, webdriver):
        super().__init__(db, webdriver)
        self.base_url = "https://quera.org"
        self.update_url = "https://quera.org/_next/data/<token>/fa/problemset.json"
        self.difficulty = [
            "EASY",
            "MEDIUM",
            "HARD",
        ]

    def update_table(self, data_list):
        self.db.create_table(f"""
        create table if not exists {self.name}(
            pk text,
            name text,
            solved_count int,
            difficulty text,
            tags text,
            sent int,
            PRIMARY key (pk)
        );""")
        self.db.add_row_many(self.name, data_list)

    def download_all(self):
        for i in self.difficulty:
            yield self.download_with_difficulty(i)

    def download_with_difficulty(self, diff="EASY"):
        diff = diff.upper()
        self.cproblem = self.get_problem(diff)
        url = self.make_url(self.cproblem)
        file_name = self.name + "_" + diff + ".pdf"
        file_path = config.join_path(file_name)
        file_name = self.download(url, file_name, file_path)
        return file_name, self.get_caption(self.cproblem, diff)

    def set_problem_sent(self):
        if not self.cproblem:
            return
        where = f"""
        pk = "{self.cproblem["pk"]}"
        """
        update = " sent = 1 "
        self.db.update_row(self.name, where, update)
        self.cproblem = None

    def get_token(self):
        url = self.base_url + "/problemset"
        soup = self.get_soup(url)
        for i in soup.findAll("script"):
            src = i.get("src")
            if "_buildManifest.js" in src:
                return src.split("/")[3]

        return ""

    def download(self, url, file_name, file_path):
        url = self.get_print_url(url)
        file_name = self.sdriver.download_pdf(url, file_path)
        return file_name

    def get_caption(self, problem, difficulty):
        c = f"{self.name} {difficulty}\n"
        c += f"name: {problem['name']}\n"
        c += f"solved count: {problem['solved_count']}\n"
        c += f"tags: {problem['tags']}\n"
        c = self.escape_markdown(c)
        c += f"[Problem]({self.make_url(problem)})\n"
        c += f"[Submit]({self.make_url(problem)})\n"

        return c

    def get_problem(self, difficulty):
        where = f"""
        difficulty = '{difficulty}'
        and sent = 0
        """
        order_by = " random() "
        # order_by=" solved_count desc "
        p = self.db.get_row(self.name,
                            where, order_by)
        return p

    def make_url(self, problem):
        pk = problem["pk"]
        return f"{self.base_url}/problemset/{pk}"

    def make_data(self, data):
        data_list = []
        for i in data:
            i = i["node"]
            tags = []
            for j in i["tags"]:
                tags.append(j["name"])
            tags = "-".join(tags)
            data_list.append({
                "pk": i["pk"],
                "name": i["name"],
                "solved_count": i["solved_count"],
                "difficulty": i["difficulty"],
                "tags": tags,
                "sent": "0",
            })
        return data_list

    def get_data(self):
        token = self.get_token()
        up_url = self.update_url.replace("<token>", token)
        data = []
        i = 1
        while True:
            url = f"{up_url}?page={i}"
            r = requests.get(url, timeout=120)
            if r.status_code != 200:
                continue

            nodes = r.json()["pageProps"]["problems"]["edges"]
            if len(nodes) == 0:
                break
            data.extend(nodes)
            i += 1
        return data

    def get_print_url(self, url):
        soup = self.get_soup(url)
        u = None
        for i in soup.find_all("a", class_="chakra-link", href=True):
            if i["href"][-5:] == "print":
                u = self.base_url + i["href"]

        return u

    def get_soup(self, url):
        r = requests.get(url, timeout=120)
        return BeautifulSoup(r.text, "html.parser")

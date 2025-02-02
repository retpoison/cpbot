import requests
from wkhtmltopdf import wkhtmltopdf

from competitive_programming import CP
import config


class CodeForces(CP):
    def __init__(self, db, webdriver):
        super().__init__(db, webdriver)
        self.base_url = "https://codeforces.com"
        self.update_url = self.base_url + "/api/problemset.problems"
        self.difficulty = {
            "easy": (500, 1600),
            "medium": (1700, 2400),
            "hard": (2500, 3500),
        }

    def update_table(self, data_list):
        self.db.create_table(f"""
        create table if not exists {self.name}(
            contestId int,
            pindex text,
            name text,
            rating int,
            tags text,
            solved_count int,
            sent int,
            PRIMARY key (contestId, pindex)
        );""")
        self.db.add_row_many(self.name, data_list)

    def download_all(self):
        for i in self.difficulty:
            yield self.download_with_difficulty(i)

    def download_with_difficulty(self, diff="easy"):
        self.cproblem = self.get_problem(diff)
        url = self.make_url("problem", self.cproblem)
        file_name = self.name + "_" + diff + ".pdf"
        file_path = config.join_path(file_name)
        file_name = self.download(url, file_name, file_path)
        return file_name, self.get_caption(self.cproblem, diff)

    def set_problem_sent(self):
        if not self.cproblem:
            return
        where = f"""
        contestId = {self.cproblem["contestId"]} and
        pindex = "{self.cproblem["pindex"]}"
        """
        update = " sent = 1 "
        self.db.update_row(self.name, where, update)
        self.cproblem = None

    def download(self, url, file_name, file_path):
        try:
            wkhtmltopdf(url=url, output_file=file_path)
        except BaseException as e:
            print("wkhtmltopdf error:", e)
            file_name = self.sdriver.download_pdf(url, file_path)
        return file_name

    def get_caption(self, problem, difficulty):
        c = f"{self.name} {difficulty}\n"
        c += f"name: {problem['name']}\n"
        c += f"solved count: {problem['solved_count']}\n"
        c += f"tags: {problem['tags']}\n"
        c = self.escape_markdown(c)
        c += f"[Problem]({self.make_url('problem', problem)})\n"
        c += f"[Submit]({self.make_url('submit', problem)})\n"

        return c

    def get_problem(self, difficulty):
        where = f"""
        rating >= {self.difficulty[difficulty][0]}
        and rating <= {self.difficulty[difficulty][1]}
        and sent = 0
        """
        order_by = " random() "
        # order_by=" solved_count desc "
        p = self.db.get_row(self.name,
                            where, order_by)
        return p

    def make_url(self, url_type, problem):
        if url_type not in ["problem", "submit"]:
            return None
        contest_id = problem["contestId"]
        pindex = problem["pindex"]
        return f"{self.base_url}/problemset/{url_type}/{contest_id}/{pindex}"

    def get_solved_count(self, data, cid, ind):
        for i in data:
            if i["contestId"] == cid and i["index"] == ind:
                return i["solvedCount"]
        return "0"

    def make_data(self, data):
        data_list = []
        for i in data["result"]["problems"]:
            if "rating" not in list(i.keys()):
                continue
            i["tags"] = "-".join(i["tags"])

            data_list.append(
                {
                    "contestId": i["contestId"],
                    "pindex": i["index"],
                    "name": i["name"],
                    "rating": i["rating"],
                    "tags": i["tags"],
                    "solved_count": self.get_solved_count(
                        data["result"]["problemStatistics"],
                        i["contestId"],
                        i["index"]),
                    "sent": "0"
                }
            )
        return data_list

    def get_data(self):
        r = requests.get(self.update_url, timeout=120)
        if r.status_code == 200:
            return r.json()
        return None

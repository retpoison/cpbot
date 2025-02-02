
class CP():
    def __init__(self, db, webdriver):
        self.name = self.__class__.__name__
        self.db = db
        self.sdriver = webdriver
        self.cproblem = None

    def update(self):
        print(f"geting data from {self.name}")
        data = self.get_data()
        print(f"geting data from {self.name} done")
        if data is None:
            print(f"{self.name} update failed")
            return
        print(f"making {self.name} data")
        data_list = self.make_data(data)
        print(f"making {self.name} data done")
        print(f"writing {self.name} data")
        self.update_table(data_list)
        print(f"writing {self.name} data done")

    def escape_markdown(self, s):
        e = ['_', '*', '[', ']', '(', ')', '~', '`', '>',
             '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for i in e:
            s = s.replace(i, '\\' + i)
        return s

    def get_current_problem(self):
        return self.cproblem

    def get_caption(self, problem, diff):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError

    def make_data(self, data):
        raise NotImplementedError

    def update_table(self, data_list):
        raise NotImplementedError

    def download_with_difficulty(self):
        raise NotImplementedError

    def set_problem_sent(self):
        raise NotImplementedError

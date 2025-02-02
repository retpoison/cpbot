
class Status:
    def __init__(self, db):
        self.name = self.__class__.__name__
        self.db = db
        self.db.create_table(f"""
        create table if not exists {self.name}(
            cp text,
            difficulty text,
            filename text,
            problem text,
            download int,
            send int
        );""")

    def add_cp(self, cp, diff):
        data = {"cp": cp, "difficulty": diff,
                "filename": "", "download": 0,
                "send": 0}
        self.db.add_row(self.name, data)

    def set_filename(self, cp, diff, filename):
        where = self.get_where(cp, diff)
        update = f"""
        filename = "{filename}"
        """
        self.db.update_row(self.name, where, update)

    def set_problem(self, cp, diff, problem):
        where = self.get_where(cp, diff)
        update = f"""
        problem = "{problem}"
        """
        self.db.update_row(self.name, where, update)

    def set_download(self, cp, diff):
        where = self.get_where(cp, diff)
        update = " download = 1 "
        self.db.update_row(self.name, where, update)

    def set_send(self, cp, diff):
        where = self.get_where(cp, diff)
        update = " send = 1 "
        self.db.update_row(self.name, where, update)

    def is_downloaded(self, cp, diff):
        r = self.get_cp(cp, diff)
        return r.get('download', 0)

    def is_sent(self, cp, diff):
        r = self.get_cp(cp, diff)
        return r.get('send', 0)

    def get_filename(self, cp, diff):
        r = self.get_cp(cp, diff)
        return r.get('filename', None)

    def get_problem(self, cp, diff):
        r = self.get_cp(cp, diff)
        return r.get('problem', None)

    def is_in_table(self, cp, diff):
        r = self.get_cp(cp, diff)
        if len(r) == 0:
            return False
        return True

    def get_cp(self, cp, diff):
        where = self.get_where(cp, diff)
        order_by = " NULL "
        return self.db.get_row(self.name, where, order_by)

    def get_where(self, cp, diff):
        return f"""
        cp = "{cp}" and
        difficulty = "{diff}"
        """

    def clear_table(self):
        self.db.clear_table(self.name)

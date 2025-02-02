import sqlite3


class Database:
    def __init__(self, path="data.db"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.curs = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    def create_table(self, table):
        self.curs.execute(table)
        self.conn.commit()

    def add_row(self, table, data_dict):
        if isinstance(data_dict, list):
            self.add_row_many(table, data_dict)
            return
        k, v = self.get_data_comma_separate(data_dict)
        self.curs.execute(f"""
        insert or ignore into {table}
        ({k})
        values ({v});""", data_dict)
        self.conn.commit()

    def add_row_many(self, table, data_list):
        k, v = self.get_data_comma_separate(data_list[0])
        self.curs.executemany(f"""
        insert or ignore into {table}
        ({k})
        values ({v});""", data_list)
        self.conn.commit()

    def get_row(self, table, where, order_by):
        if not where:
            where = "1=1"

        self.curs.execute(f"""
                select * from {table}
                where {where}
                order by {order_by};
                              """)
        return self.data_to_dict(self.curs.fetchone())

    def update_row(self, table, where, update):
        if not update or not where:
            return
        self.curs.execute(f"""
                update {table}
                set {update}
                where {where}""")
        self.conn.commit()

    def get_result(self, q):
        self.curs.execute(q)
        return self.data_to_dict(self.curs.fetchall())

    def is_table_exist(self, table_name):
        q = """SELECT count(name) as exist
        FROM sqlite_master
        WHERE type = "table" AND name = ? """

        self.curs.execute(q, (table_name,))
        return self.data_to_dict(self.curs.fetchone())["exist"]

    def data_to_dict(self, data):
        if data is None:
            return {}
        if isinstance(data, list):
            data_dict = [{k: item[k] for k in item.keys()} for item in data]
        else:
            data_dict = {k: data[k] for k in data.keys()}
        return data_dict

    def get_data_comma_separate(self, data_dict):
        k = ", ".join(data_dict.keys())
        v = ":" + ", :".join(data_dict.keys())
        return k, v

    def clear_table(self, table_name):
        self.curs.execute(f"delete from {table_name}")
        self.conn.commit()

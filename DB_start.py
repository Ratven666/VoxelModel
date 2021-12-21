import sqlite3
import os.path


class Project:

    __tables = {
        "points_table": """CREATE TABLE IF NOT EXISTS points (
                            id INTEGER PRIMARY KEY,
                            X REAL,
                            Y REAL,
                            Z REAL,
                            R INTEGER DEFAULT NULL,
                            G INTEGER DEFAULT NULL,
                            B INTEGER DEFAULT NULL,
                            nX INTEGER DEFAULT NULL,
                            nY INTEGER DEFAULT NULL,
                            nZ INTEGER DEFAULT NULL
                            );""",

        "scans_table": """CREATE TABLE IF NOT EXISTS scans (
                            id INTEGER PRIMARY KEY,
                            name VARCHAR(255) UNIQUE NOT NULL,
                            len INTEGER DEFAULT 0,
                            min_X REAL DEFAULT NULL,
                            max_X REAL DEFAULT NULL,
                            min_Y REAL DEFAULT NULL,
                            max_Y REAL DEFAULT NULL,
                            created_at DATETIME DEFAULT (DATETIME('now', 'localtime'))
                            );""",

        "points_scans_table": """CREATE TABLE IF NOT EXISTS points_scans (
                                point_id BIGINT UNSIGNED NOT NULL,
                                scan_id BIGINT UNSIGNED NOT NULL,
                                PRIMARY KEY (point_id, scan_id), 
                                FOREIGN KEY (point_id) REFERENCES points(id) ON UPDATE CASCADE ON DELETE CASCADE,
                                FOREIGN KEY (scan_id) REFERENCES scans(id) ON UPDATE CASCADE ON DELETE CASCADE
                                );""",

        "imported_files_table": """CREATE TABLE IF NOT EXISTS imported_files (
                                    id INTEGER PRIMARY KEY,
                                    name VARCHAR(255) NOT NULL,
                                    scan_id BIGINT UNSIGNED NOT NULL,
                                    FOREIGN KEY (scan_id) REFERENCES scans(id) ON UPDATE CASCADE ON DELETE CASCADE
                                    );"""
        }

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.__sqlite_connection = None
        self.__cursor = None
        self.init_db()

    def __enter__(self):
        path = os.path.join("data_bases", f"{self.project_name}.db")
        self.__sqlite_connection = sqlite3.connect(path)
        self.__cursor = self.__sqlite_connection.cursor()
        return self.__cursor

    def __exit__(self, type, value, traceback):
        self.__sqlite_connection.commit()
        self.__cursor.close()

    @property
    def sqlite_connection(self):
        path = os.path.join("data_bases", f"{self.project_name}.db")
        return sqlite3.connect(path)

    def init_db(self):
        with self as db:
            for table in Project.__tables.values():
                db.execute(table)


if __name__ == "__main__":
    pr = Project("test")

    with pr as p:
        p.execute("""SELECT * FROM points""").fetchall()
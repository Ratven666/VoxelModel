from DB_start import *
from DB_Point import *
from DB_ScanItterator import *


class Scan:

    def __init__(self, project, name: str):
        self.project = project
        self.name = name
        self.scan_id = self.__init_scan()
        self.len = None
        self.borders = None

    def __iter__(self):
        return iter(ScanItterator(self))

    def __len__(self):
        return self.len

    def __init_scan(self):
        with self.project as project:
            result = project.execute("SELECT s.id FROM scans s WHERE s.name = (?)", (self.name,)).fetchone()
            if result is None or len(result) == 0:
                scan_id = project.execute("""INSERT INTO scans (name) VALUES
                                                (?);
                                                """, (self.name,)).lastrowid
            else:
                scan_id = result[0]
            return scan_id

    def __calc_scan_metrics(self):
        with self.project as project:
            result = project.execute("""SELECT COUNT(p.id), MIN(p.X), MAX(p.X), MIN(p.Y), MAX(p.Y) FROM points p
                            JOIN points_scans ps ON ps.point_id = p.id
                            WHERE ps.scan_id = (?)""", (self.scan_id,)).fetchone()
            self.len = result[0]
            self.borders = {"min_X": result[1], "max_X": result[2], "min_Y": result[3], "max_Y": result[4]}

    def add_point_to_scan(self, point: Point):
        with self.project as project:
            if len(pr.execute("""SELECT p.id FROM points p WHERE p.id = (?)""",
                              (point.point_id, )).fetchone()) == 1:
                project.execute("INSERT INTO points_scans (point_id, scan_id) VALUES (?, ?)",
                                (point.point_id, self.scan_id))
            else:
                last_point_id = project.execute("""SELECT id FROM points ORDER BY id DESC LIMIT 1 """).fetchone()
                if last_point_id is None:
                    point_id = 0
                else:
                    point_id = last_point_id[0] + 1
                project.execute("""INSERT INTO points (X, Y, Z, R, G, B, nX, nY, nZ, id) 
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (point.x, point.y, point.z,
                                 point.color[0], point.color[1], point.color[2],
                                 point.normal[0], point.normal[1], point.normal[2],
                                 point_id))
                project.execute("INSERT INTO points_scans (point_id, scan_id) VALUES (?, ?)",
                                (point_id, self.scan_id))
        self.__update_borders(point)
        self.len += 1

    def __update_borders(self, point: Point):
        x, y = point.x, point.y
        if self.len == 0:
            self.borders = {"min_X": x, "max_X": x, "min_Y": y, "max_Y": y}
            return
        if x < self.borders["min_X"]:
            self.borders["min_X"] = x
        if x > self.borders["max_X"]:
            self.borders["max_X"] = x
        if y < self.borders["min_Y"]:
            self.borders["min_Y"] = y
        if y > self.borders["max_Y"]:
            self.borders["max_Y"] = y

    def parse_points_from_file(self, path_to_file: str, point_n=1000):
        with self.project as project:
            file_flag = project.execute("""SELECT if.id FROM imported_files if WHERE if.name = (?)""",
                                    (path_to_file,)).fetchone()
            if file_flag is not None and len(file_flag) == 1:
                print("Такой файл уже загружен!!!")
                return

            def insert_data_to_db(points_lst: list, id_points_scan: list):
                if len(points_lst[0]) == 4:
                    project.executemany("INSERT INTO points (X, Y, Z, id) VALUES (?, ?, ?, ?)", points_lst)
                elif len(points_lst[0]) == 7:
                    project.executemany("""INSERT INTO points (X, Y, Z, R, G, B, id) 
                                            VALUES (?, ?, ?, ?, ?, ?, ?)""", points_lst)
                elif len(points_lst[0]) == 10:
                    project.executemany("""INSERT INTO points (X, Y, Z, R, G, B, nX, nY, nZ, id) 
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", points_lst)
                else:
                    raise ValueError("Не верный формат файла")
                project.executemany("INSERT INTO points_scans (point_id, scan_id) VALUES (?, ?)", id_points_scan)

            last_point_id = project.execute("""SELECT id FROM points ORDER BY id DESC LIMIT 1 """).fetchone()
            if last_point_id is None:
                last_point_id = 0
            else:
                last_point_id = last_point_id[0]

            points = []
            id_point_scan = []
            with open(path_to_file, "r") as file:
                for line in file:
                    point = [float(lst) for lst in line.strip().split(" ")]
                    last_point_id += 1
                    point.append(last_point_id)
                    points.append(tuple(point))
                    id_point_scan.append((last_point_id, self.scan_id))
                    if len(points) == point_n:
                        insert_data_to_db(points, id_point_scan)
                        points = []
                        id_point_scan = []
                try:
                    insert_data_to_db(points, id_point_scan)
                except sqlite3.OperationalError:
                    pass
            project.execute("INSERT INTO imported_files (name, scan_id) VALUES (?, ?)", (path_to_file, self.scan_id))
        self.__calc_scan_metrics()



if __name__ == "__main__":
    import time

    pr = Project("s12")

    # with pr as pr:
    #     rez = pr.execute("SELECT s.id FROM scans s WHERE s.name = '1q'").fetchone()
    #     print(rez)

    sc1 = Scan(pr, "KuchaRGB")
    t0 = time.time()
    sc1.parse_points_from_file(os.path.join("src", "15_1248.txt"))
    # print(time.time() - t0)
    # #
    # # t0 = time.time()
    # # with pr as p:
    # #     print(p.execute("""SELECT id, X, y, z FROM points ORDER BY x DESC LIMIT 100 """).fetchall())
    # # print(time.time() - t0)
    #
    # # t0 = time.time()
    # # with pr as p:
    # #     # print(p.execute("""SELECT MIN(X), MAX(X), MIN(Y), MAX(Y) FROM points""").fetchall())
    # #     print(p.execute("""SELECT MIN(X), MAX(X), MIN(Y), MAX(Y) FROM points""").fetchall())
    # #
    # # print(time.time() - t0)
    t0 = time.time()
    print(t0)
    print(time.time() - t0)
    # n = 0
    # for p in sc1:
    #     print(p)
    # print(n)
    # print(time.time() - t0)
    with pr as pr:
        r = pr.execute("""SELECT p.id FROM points p WHERE p.id = 120""").fetchone()
    print(r)
    print(time.time() - t0)
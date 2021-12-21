import matplotlib.pyplot as plt

from DB_start import *
from DB_Point import *
from DB_ScanItterator import *


class Scan:

    def __init__(self, project, name: str):
        self.project = project
        self.name = name
        self.len = 0
        self.borders = None
        self.scan_id = self.__init_scan()

        # self.__calc_scan_metrics()

    def __iter__(self):
        return iter(ScanItterator(self))

    def __len__(self):
        return self.len

    def __init_scan(self):
        with self.project as project:
            result = project.execute("""SELECT s.id, s.len, s.min_X, s.max_X,
                                                s.min_Y, s.max_Y
                                                FROM scans s WHERE s.name = (?)""", (self.name,)).fetchone()
            if result is None or len(result) == 0:
                scan_id = project.execute("""INSERT INTO scans (name) VALUES
                                                (?);
                                                """, (self.name,)).lastrowid
            else:
                scan_id = result[0]
                self.len = result[1]
                self.borders = {"min_X": result[2], "max_X": result[3], "min_Y": result[4], "max_Y": result[5]}
            return scan_id

    def __calc_scan_metrics(self):
        with self.project as project:
            result = project.execute("""SELECT COUNT(p.id), MIN(p.X), MAX(p.X), MIN(p.Y), MAX(p.Y) FROM points p
                            JOIN points_scans ps ON ps.point_id = p.id
                            WHERE ps.scan_id = (?)""", (self.scan_id,)).fetchone()
            self.len = result[0]
            self.borders = {"min_X": result[1], "max_X": result[2], "min_Y": result[3], "max_Y": result[4]}

    def __update_scan_metrics_in_db(self):
        with self.project as project:
            project.execute("""UPDATE scans SET 
                                    len = (?),
                                    min_X = (?), max_X = (?),
                                    min_Y = (?), max_Y = (?) 
                                    WHERE id = (?)
                                    ;""", (self.len, self.borders["min_X"], self.borders["max_X"],
                                           self.borders["min_Y"], self.borders["max_Y"],
                                           self.scan_id))

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
        self.len += 1
        if self.__update_borders(point):
            self.__update_scan_metrics_in_db()

    def __update_borders(self, point: Point):
        x, y = point.x, point.y
        update_flag = False
        if self.len == 1:
            self.borders = {"min_X": x, "max_X": x, "min_Y": y, "max_Y": y}
            update_flag = True
            return update_flag
        if x < self.borders["min_X"]:
            self.borders["min_X"] = x
            update_flag = True
        if x > self.borders["max_X"]:
            self.borders["max_X"] = x
            update_flag = True
        if y < self.borders["min_Y"]:
            self.borders["min_Y"] = y
            update_flag = True
        if y > self.borders["max_Y"]:
            self.borders["max_Y"] = y
            update_flag = True
        return update_flag

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
        self.__update_scan_metrics_in_db()

    def plot(self, max_point_count=10_000):
        x_lst, y_lst, z_lst, c_lst = [], [], [], []
        if len(self) < max_point_count:
            step = 1
        else:
            step = int(len(self) / max_point_count)
        count = 0
        for point in self:
            if count == 0:
                x_lst.append(point.x)
                y_lst.append(point.y)
                z_lst.append(point.z)
                if point.color == (None, None, None):
                    c_lst.append((0, 0, 0))
                else:
                    c_lst.append([el / 255.0 for el in point.color])
            count += 1
            if count == step:
                count = 0
        min_x, min_y, min_z = self.borders["min_X"], self.borders["min_Y"], min(z_lst)
        max_x, max_y, max_z = self.borders["max_X"], self.borders["max_Y"], max(z_lst)

        limits = [max_x - min_x,
                  max_y - min_y,
                  max_z - min_z]
        length = max(limits) / 2
        x_lim = [((min_x + max_x)/2) - length, ((min_x + max_x)/2) + length]
        y_lim = [((min_y + max_y)/2) - length, ((min_y + max_y)/2) + length]
        z_lim = [((min_z + max_z)/2) - length, ((min_z + max_z)/2) + length]

        px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
        fig = plt.figure(figsize=(800 * px, 800 * px))
        ax = fig.add_subplot(projection="3d")
        ax.set_xlim(*x_lim)
        ax.set_ylim(*y_lim)
        ax.set_zlim(*z_lim)
        ax.scatter(x_lst, y_lst, z_lst, c=c_lst, marker="+", s=2)

        plt.show()

if __name__ == "__main__":
    import time

    pr = Project("15")

    # with pr as pr:
    #     rez = pr.execute("SELECT s.id FROM scans s WHERE s.name = '1q'").fetchone()
    #     print(rez)

    sc1 = Scan(pr, "15")
    t0 = time.time()
    sc1.parse_points_from_file(os.path.join("src", "15.txt"))
    print(time.time() - t0)

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
    sc1.plot(25000)
    print(time.time() - t0)



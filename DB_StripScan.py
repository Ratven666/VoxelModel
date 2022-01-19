from os import remove

from DB_Line2D import *


class StripScan(Scan):

    def __init__(self, project: Project, line: Line2D, width: (int, float)):
        name = f"{str(line)} - {width}"
        super().__init__(project, name)
        self.line = line
        self.width = width

    def __str__(self):
        return f"StripScan name = {self.name}\n\t" \
               f"point count = {len(self)}"

    def __repr__(self):
        return self.__str__()

    def parse_points_from_file(self, path_to_file: str, point_n=1000):
        """Парсит файл с точками в БД"""
        with self.project as project:
            """Проверяет был ли загружен уже этот файл в скан"""
            #  Выполнить проверку на присутствие конкретного файла в конкретном скане !!!!!!!!!!!!!!!
            file_flag = project.execute("""SELECT if.id FROM imported_files if WHERE if.name = (?)
                                                                                    AND if.scan_id = (?)""",
                                                                    (path_to_file, self.scan_id)).fetchone()
            if file_flag is not None and len(file_flag) == 1:
                print("Такой файл уже загружен!!!")  # Грязь!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                return

            def insert_data_to_db(points_lst: list, id_points_scan: list):
                """Пакетно загружает в БД точки в таблицы points и points_scans"""
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
                for row in file:
                    point = [float(lst) for lst in row.strip().split(" ")]
                    p = Point(point[0], point[1])
                    if self.line.distance_from_point_to_line(Point(point[0], point[1])) <= self.width:
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
        self.calc_scan_metrics()
        self.update_scan_metrics_in_db()

    def add_point_to_scan(self, point: Point):
        if self.line.distance_from_point_to_line(point) <= self.width:
            super(StripScan, self).add_point_to_scan(point)

    @classmethod
    def cut_scan(cls, line2D: Line2D, width: (int, float), scan: Scan, force_cat=False):
        temp_strip_scan = cls(scan.project, line2D, width)
        if temp_strip_scan.len != 0 and force_cat is False:
            print("Уже есть!")
            return temp_strip_scan
        with open("temp_file.txt", "w") as file:
            for point in scan:
                if line2D.distance_from_point_to_line(point) <= width:
                    file.write(f"{point.point_id}, {temp_strip_scan.scan_id}\n")
        point_n = 100000
        id_point_scan = []
        with Project("") as project:
            with open("temp_file.txt", "r") as file:
                for line in file:
                    data = [int(p_ps) for p_ps in line.strip().split(",")]
                    id_point_scan.append(tuple(data))
                    if len(id_point_scan) == point_n:
                        project.executemany("INSERT OR IGNORE INTO points_scans (point_id, scan_id) VALUES (?, ?)",
                                            id_point_scan)
                        id_point_scan = []
                try:
                    project.executemany("INSERT OR IGNORE INTO points_scans (point_id, scan_id) VALUES (?, ?)",
                                        id_point_scan)
                except sqlite3.OperationalError:
                    pass
        remove("temp_file.txt")
        temp_strip_scan.calc_scan_metrics()
        temp_strip_scan.update_scan_metrics_in_db()
        return temp_strip_scan


if __name__ == "__main__":
    pr = Project("Line")

    sc15 = Scan(pr, "Kucha")

    sc15.parse_points_from_file(os.path.join("src", "KuchaRGB.txt"))

    # sc15.plot()

    p1 = Point(-4, -23)
    p2 = Point(-4, -0.4)

    line = Line2D(p1, p2)
    # #
    str_sc15_2 = StripScan.cut_scan(line, 2, sc15)
    str_sc15_1 = StripScan.cut_scan(line, 1, sc15)
    str_sc15_3 = StripScan(pr, line, 3)
    str_sc15_3.parse_points_from_file(os.path.join("src", "KuchaRGB.txt"))

    str_sc15_1.plot()

    print(line)

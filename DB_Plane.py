import numpy as np

from DB_Scan import *


class Plane:

    def __init__(self, plane_id=None):
        self.len = 0
        self.a = None
        self.b = None
        self.c = None
        self.d = None
        self.plane_id = self.__init_plane(plane_id)

    def __str__(self):
        return f"Поверхность \"{self.plane_id}\":\n" \
               f"\tA = {self.a}\n" \
               f"\tB = {self.b}\n" \
               f"\tC = {self.c}\n" \
               f"\tD = {self.d}\n"

    def __init_plane(self, plane_id):
        """Проверяет присутствие плоскости с таким id в БД
                в случае наличия сохраняет данные из БД в объект
                в случае отсутствия - создает новую запись в БД"""
        connection = Project("").sqlite_connection
        cursor_inn = connection.cursor()
        try:
            plane_data = cursor_inn.execute("""SELECT p.id, p.len, 
                                                   p.A, p.B, p.C, p.D
                                                   FROM planes p WHERE p.id = (?)""", (plane_id,)).fetchone()
            if plane_data is None or len(plane_data) == 0:
                plane_id = cursor_inn.execute("""INSERT INTO planes (len, A, B, C, D) VALUES
                                                    (?, ?, ?, ?, ?);
                                                    """, (self.len, self.a, self.b, self.c, self.d)).lastrowid
            else:
                plane_id = plane_data[0]
                self.len = plane_data[1]
                self.a, self.b, self.c, self.d = plane_data[2], plane_data[3], plane_data[4], plane_data[5]
        finally:
            connection.commit()
            cursor_inn.close()
        return plane_id

    def is_calculated(self):
        if None in (self.a, self.b, self.c, self.d):
            return False
        else:
            return True

    def __update_plane_data_in_db(self):
        """Обновдяет данные плоскости в БД на основании атрибутов объекта"""
        with Project("") as cursor_inn:
            cursor_inn.execute("""UPDATE planes SET
                                    len = (?),
                                    A = (?), B = (?),
                                    C = (?), D = (?)
                                    WHERE id = (?)
                                    ;""", (self.len, self.a, self.b,
                                           self.c, self.d,
                                           self.plane_id))

    def distance_calc(self, point: Point):
        return (abs((self.a * point.x) + (self.b * point.y) + (self.c * point.z) +
                    self.d) / (((self.a ** 2) + (self.b ** 2) + (self.c ** 2)) ** 0.5))

    def fit_plane_to_scan(self, scan: Scan, force_fit=False):
        if self.__check_scan(scan) and force_fit is False:
            return

        if len(scan) < 3:
            return None

        xyz = np.array([[point.x, point.y, point.z] for point in scan])
        a1, b1, c1, d1, b2, c2, c3, d1, d2, d3 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        for point in xyz:
            a1 += point[0] ** 2
            b1 += point[0] * point[1]
            c1 += point[0]
            b2 += point[1] ** 2
            c2 += point[1]
            c3 += 1
            d1 += point[0] * point[2]
            d2 += point[1] * point[2]
            d3 += point[2]
        mA = np.array([[a1, b1, c1], [b1, b2, c2], [c1, c2, c3]])
        mD = np.array([d1, d2, d3])
        try:
            abc = np.linalg.solve(mA, mD)
        except np.linalg.LinAlgError:
            return None
        self.len = len(scan)
        self.a = float(abc[0])
        self.b = float(abc[1])
        self.c = -1.0
        self.d = float(abc[2])
        self.__update_plane_data_in_db()
        return None

    def __check_scan(self, scan: Scan):
        return scan.len == self.len
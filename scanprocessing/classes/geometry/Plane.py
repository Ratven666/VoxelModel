import numpy as np

from scanprocessing.classes.Scan import *


class Plane:
    counter = 0

    def __init__(self, a: float, b: float, c: float, d: float):
        Plane.counter += 1
        self.id = Plane.counter
        self.number_of_points = 0
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)
        self.d = float(d)

    def __str__(self):
        return f"Поверхность \"{self.id}\":\n" \
               f"\tA = {self.a}\n" \
               f"\tB = {self.b}\n" \
               f"\tC = {self.c}\n" \
               f"\tD = {self.d}\n"

    def distance_calc(self, point: Point):
        return (abs((self.a * point.x) + (self.b * point.y) + (self.c * point.z) +
                    self.d) / (((self.a ** 2) + (self.b ** 2) + (self.c ** 2)) ** 0.5))

    @staticmethod
    def fit_plane_to_point_arr(scan: Scan):
        if len(scan.points) < 3:
            return None

        xyz = np.array([[i.x, i.y, i.z] for i in scan.points])

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

        temp_plane = Plane(0, 0, 0, 0)
        temp_plane.number_of_points = len(scan.points)
        temp_plane.a = float(abc[0])
        temp_plane.b = float(abc[1])
        temp_plane.c = -1.0
        temp_plane.d = float(abc[2])
        return temp_plane

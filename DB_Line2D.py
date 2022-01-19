from DB_Scan import *
import numpy as np


class Line2D:

    def __init__(self, start_point: (Point, None), end_point: (Point, None)):
        self.start_point = start_point
        self.end_point = end_point
        self.parameters = self.__calk_line_parameters()

    def __str__(self):
        a, b, c = self.parameters["A"], self.parameters["B"], self.parameters["C"]
        return f"Line2D: {a}x+{b}y+{c}=0"

    @classmethod
    def create_line_from_equation(cls, a: float, b: float, c: float):
        temp_line = cls(None, None)
        temp_line.parameters = {"A": a, "B": b, "C": c}
        return temp_line

    @classmethod
    def fit_line_to_2d_scan(cls, scan: Scan):
        aa, ab, bb, al, bl = 0, 0, 0, 0, 0
        for point in scan.points:
            x, y = point.x, point.y
            aa += x ** 2
            ab += x
            bb += 1
            al += x * y
            bl += y
        # k = (bl*ab - al*bb) / (aa*bb - ab*ab)
        # b = -(bl + ab*k) / bb
        #
        # ax = (bb * al - bl * ab) / (ab * ab - aa * bb)
        # ay = (-al - aa * ax) / ab
        #
        # print(ax, ay)

        mA = np.array([[aa, ab], [ab, bb]])
        mD = np.array([al, bl])
        try:
            kb = np.linalg.solve(mA, mD)
        except np.linalg.LinAlgError:
            return None
        # print(kb)
        # print(k, b)
        return cls.create_line_from_equation(-kb[0], 1.0, -kb[1])

        # return cls.create_line_from_equation(-k, 1.0, -b)

    def calk_point_on_line(self, point: Point, in_line=True):
        a_1 = self.parameters["A"]
        b_1 = self.parameters["B"]
        c_1 = self.parameters["C"]

        a_2 = -b_1
        b_2 = a_1
        c_2 = b_1 * point.x - a_1 * point.y

        x = (b_2*c_1 - c_2*b_1) / (a_2*b_1 - a_1*b_2)
        y = (-c_1 - a_1*x) / b_1

        if in_line is True:
            if self.__is_point_in_line_limit(point) is True:
                return Point(x, y, point.z)
            else:
                return
        else:
            return Point(x, y, point.z)

    def __is_point_in_line_limit(self, point: Point):
        x_min = min(self.start_point.x, self.end_point.x)
        x_max = max(self.start_point.x, self.end_point.x)
        y_min = min(self.start_point.y, self.end_point.y)
        y_max = max(self.start_point.y, self.end_point.y)
        if x_min <= point.x <= x_max and y_min <= point.y <= y_max:
            return True
        else:
            return False

    def __calk_line_parameters(self):
        if self.start_point is None and self.end_point is None:
            return None
        x1, y1 = self.start_point.x, self.start_point.y
        x2, y2 = self.end_point.x, self.end_point.y
        a = y1 - y2
        b = x2 - x1
        c = x1 * y2 - x2 * y1
        return {"A": a, "B": b, "C": c}

    def distance_from_point_to_line(self, point: Point):
        x, y = point.x, point.y
        a, b, c = self.parameters["A"], self.parameters["B"], self.parameters["C"]
        dist = abs(a*x + b*y + c) / ((a**2 + b**2)**0.5)
        return dist

    def line_dist(self):
        x_st, y_st = self.start_point.x, self.start_point.y
        x_ed, y_ed = self.end_point.x, self.end_point.y
        return ((x_st - x_ed)**2 + (y_st - y_ed)**2) ** 0.5

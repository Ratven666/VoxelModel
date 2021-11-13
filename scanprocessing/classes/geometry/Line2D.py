from .Point import *


class Line2D:

    def __init__(self, start_point: Point, end_point: Point):
        self.start_point = start_point
        self.end_point = end_point
        self.parameters = self.__calk_line_parameters()

    def __str__(self):
        a, b, c = self.parameters["A"], self.parameters["B"], self.parameters["C"]
        return f"Line2D: {a}x+{b}y+{c} = 0"

    def __calk_line_parameters(self):
        x1, y1 = self.start_point.x, self.start_point.y
        x2, y2 = self.end_point.x, self.end_point.y
        a = y1 - y2
        b = x2 - x1
        c = x1 * y2 - x2 * y1
        return {"A": a, "B": b, "C": c}

    def distance_calc(self, point: Point):
        x, y = point.x, point.y
        a, b, c = self.parameters["A"], self.parameters["B"], self.parameters["C"]
        dist = abs(a*x + b*y + c) / ((a**2 + b**2)**0.5)
        return dist

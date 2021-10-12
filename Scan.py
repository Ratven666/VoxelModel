from Point import *


class Scan:

    def __init__(self, name: str):
        self.name = name
        self.points = []
        self.borders = {"lower_left": Point(float("inf"), float("inf")),
                        "upper_left": Point(-float("inf"), float("inf")),
                        "upper_right": Point(-float("inf"), -float("inf")),
                        "lower_right": Point(float("inf"), -float("inf"))
                        }

    def __len__(self):
        return len(self.points)

    def __str__(self):
        return f"Scan name = {self.name}\n\t" \
               f"point count = {len(self)}"

    def add_point_to_scan(self, point: Point):
        self.points.append(point)
        self.__calk_scan_borders(point)

    def __calk_scan_borders(self, point: Point):
        if point.x < self.borders["lower_left"].x:
            self.borders["lower_left"] = Point(point.x, self.borders["lower_left"].y)
            self.borders["upper_left"] = Point(point.x, self.borders["upper_left"].y)
        if point.x > self.borders["upper_right"].x:
            self.borders["lower_right"] = Point(point.x, self.borders["lower_right"].y)
            self.borders["upper_right"] = Point(point.x, self.borders["upper_right"].y)

        if point.y < self.borders["lower_left"].y:
            self.borders["lower_left"] = Point(self.borders["lower_left"].x, point.y)
            self.borders["lower_right"] = Point(self.borders["lower_right"].x, point.y)
        if point.y > self.borders["upper_right"].y:
            self.borders["upper_left"] = Point(self.borders["upper_left"].x, point.y)
            self.borders["upper_right"] = Point(self.borders["upper_right"].x, point.y)


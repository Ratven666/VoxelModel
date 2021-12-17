from scanprocessing.classes.Scan import *
from scanprocessing.classes.geometry.Line2D import *


class StripScan(Scan):

    def __init__(self, line: Line2D, width: (int, float)):
        name = f"{str(line)} - {width}"
        super().__init__(name)
        self.line = line
        self.width = width

    def __str__(self):
        return f"StripScan name = {self.name}\n\t" \
               f"point count = {len(self)}"

    def __repr__(self):
        return self.__str__()

    def add_point_to_scan(self, point: Point):
        if self.line.distance_from_point_to_line(point) <= self.width:
            self.points.append(point)
            self._Scan__calk_scan_borders(point)

    @classmethod
    def cut_scan(cls, line: Line2D, width: (int, float), scan: Scan):
        temp_strip_scan = cls(line, width)
        for point in scan.points:
            temp_strip_scan.add_point_to_scan(point)
        return temp_strip_scan






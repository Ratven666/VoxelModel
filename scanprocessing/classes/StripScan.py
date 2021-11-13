from scanprocessing.classes.Scan import *
from scanprocessing.classes.geometry.Line2D import *


class StripScan(Scan):

    def __init__(self, line: Line2D, width: (int, float)):
        name = f"{str(line)} - {width}"
        super().__init__(name)
        self.line = line
        self.width = width

    def add_point_to_scan(self, point: Point):
        if self.line.distance_calc(point) <= self.width:
            self.points.append(point)
            self._Scan__calk_scan_borders(point)




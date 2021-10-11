class Scan:

    def __init__(self, name: str):
        self.name = name
        self.points = []

    def add_point_to_scan(self, point: Point):
        self.points.append(point)

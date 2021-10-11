class Scan:

    def __init__(self, name: str):
        self.name = name
        self.points = []

    def __len__(self):
        return len(self.points)

    def add_point_to_scan(self, point):
        self.points.append(point)


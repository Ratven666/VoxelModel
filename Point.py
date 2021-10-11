class Point:

    total_count_point = 0

    def __init__(self, x: float, y: float, z: float):
        Point.total_count_point += 1

        self.x = x
        self.y = y
        self.z = z
        self.id = Point.total_count_point

    def __str__(self):
        return f"Point id = {self.id}\n\tx = {self.x}\n\ty = {self.y}\n\tz = {self.z}"

class Point:

    def __init__(self, x: float, y: float, z=0.0,
                 point_id=None,
                 color=(None, None, None),
                 normal=(None, None, None)):
        self.point_id = point_id
        self.x = x
        self.y = y
        self.z = z
        self.color = color
        self.normal = normal

    def __str__(self):
        return f"Point id = {self.id}\n\tx = {self.x}\n\ty = {self.y}\n\tz = {self.z}"

    @classmethod
    def parse_point_from_db(cls, data: tuple):
        return Point(point_id=data[0], x=data[1], y=data[2], z=data[3],
                     color=(data[4], data[5], data[6]),
                     normal=(data[7], data[8], data[9]))

from DB_Scan import *
from DB_Point import *
from DB_Scan import *


class ScanIterator:

    def __init__(self, scan: Scan):
        self.project = scan.project
        self.scan_id = scan.scan_id
        self.cursor = None
        self.generator = None

    def __iter__(self):
        connection = self.project.sqlite_connection
        self.cursor = connection.cursor()
        self.generator = (Point.parse_point_from_db(data) for data in
                          self.cursor.execute("""SELECT p.id, p.X, p.Y, p.Z,
                                                    p.R, p.G, p.B,
                                                    p.nX, p.nY, p.nZ
                                                    FROM points p
                                                    JOIN points_scans ps ON ps.point_id = p.id
                                                    WHERE ps.scan_id = (?)""", (self.scan_id,)))
        return self.generator

    def __next__(self):
        try:
            return next(self.generator)
        except StopIteration:
            self.cursor.close()
            raise StopIteration
        finally:
            self.cursor.close()


if __name__ == "__main__":

    lst = (x for x in [1, 2, 3])

    print(lst)

    gen = iter(lst)

    print(next(lst))
    print(next(lst))
    print(next(lst))
    print(next(lst))
    print(next(lst))


from scanprocessing.classes.geometry.Plane import *
from scanprocessing.classes.VoxelLevels import *


class Voxel:

    def __init__(self, lower_left_point: Point, level=VoxelLevels.LEVELS["level_4"]):
        self.lower_left_point = lower_left_point
        self.voxel_level = level                                   # SIC!!!!!!!!!!!!!!
        self.vxl_borders = self.__calk_voxel_borders()
        self.name = f"VXL_{self.voxel_level[0]}_" \
                    f"X{round(self.lower_left_point.x, 2)}_" \
                    f"Y{round(self.lower_left_point.y, 2)}"
        self.scan = Scan(f"Scan_{self.name}")
        self.plane = None
        self.errors = None

        self.sub_voxel_model = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __calk_voxel_borders(self):
        x0 = self.lower_left_point.x
        y0 = self.lower_left_point.y
        step = self.voxel_level[0]
        return {"lower_left": Point(x0, y0),
                "upper_left": Point(x0, y0 + step),
                "upper_right": Point(x0 + step, y0 + step),
                "lower_right": Point(x0 + step, y0)
                }

    def update_vxl_z_borders(self):
        if self.plane is None:
            return
        a = self.plane.a
        b = self.plane.b
        d = self.plane.d
        for point in self.vxl_borders.values():
            point.z = a*point.x + b*point.y + d

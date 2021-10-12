from scanprocessing.classes.Scan import *
from scanprocessing.classes.VoxelLevels import *


class Voxel:

    def __init__(self, lower_left_point: Point, level=VoxelLevels.LEVELS["level_4"]):
        self.lower_left_point = lower_left_point
        self.voxel_level = level                                   # SIC!!!!!!!!!!!!!!

        self.name = f"VXL_{self.voxel_level[0]}_" \
                    f"X{round(self.lower_left_point.x, 2)}_" \
                    f"Y{round(self.lower_left_point.y, 2)}"
        self.scan = Scan(f"Scan_{self.name}")

        self.sub_voxel_model = None

    def __str__(self):
        return self.name

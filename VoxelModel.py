from Voxel import *
from VoxelLevels import *

from Point import *


class VoxelModel:

    def __init__(self, scan: Scan, vxl_lvl=VoxelLevels.LEVELS["level_4"]):
        self.name = f"VM_{scan.name}"
        self.scan = scan
        self.vxl_step = vxl_lvl[0]
        self.vxl_lvl = vxl_lvl

        self.borders = self.__calc_vxl_md_bord()
        self.vxl_model = self.__create_vxl_struct()
        self.__separate_scan_to_vxl()

    def __len__(self):
        return len(self.vxl_model) * len(self.vxl_model[0])

    def __calc_vxl_md_bord(self):  # !!!! Сделать проверку на отсутствие inf в координатах границ скана !!!!
        return {"lower_left": Voxel(Point(self.scan.borders["lower_left"].x // self.vxl_step * self.vxl_step,
                                          self.scan.borders["lower_left"].y // self.vxl_step * self.vxl_step),
                                    self.vxl_lvl),
                "upper_left": Voxel(Point(self.scan.borders["upper_left"].x // self.vxl_step * self.vxl_step,
                                          self.scan.borders["upper_left"].y // self.vxl_step * self.vxl_step),
                                    self.vxl_lvl),
                "upper_right": Voxel(Point(self.scan.borders["upper_right"].x // self.vxl_step * self.vxl_step,
                                           self.scan.borders["upper_right"].y // self.vxl_step * self.vxl_step),
                                     self.vxl_lvl),
                "lower_right": Voxel(Point(self.scan.borders["lower_right"].x // self.vxl_step * self.vxl_step,
                                           self.scan.borders["lower_right"].y // self.vxl_step * self.vxl_step),
                                     self.vxl_lvl)
                }

    def __create_vxl_struct(self):
        x_start = self.borders["lower_left"].lower_left_point.x
        y_start = self.borders["lower_left"].lower_left_point.y

        x_stop = self.borders["upper_right"].lower_left_point.x
        y_stop = self.borders["upper_right"].lower_left_point.y

        x_count = int((x_stop - x_start) / self.vxl_step)
        y_count = int((y_stop - y_start) / self.vxl_step)

        return [[Voxel(Point(x_start + x * self.vxl_step, y_start + y * self.vxl_step), self.vxl_lvl)
                 for x in range(x_count + 1)] for y in range(y_count + 1)]

    def __separate_scan_to_vxl(self):
        x_start = self.borders["lower_left"].lower_left_point.x
        y_start = self.borders["lower_left"].lower_left_point.y

        for point in self.scan.points:
            x, y = point.x, point.y
            vxl_md_X = int((x-x_start) // self.vxl_step)
            vxl_md_Y = int((y-y_start) // self.vxl_step)
            self.vxl_model[vxl_md_Y][vxl_md_X].scan.add_point_to_scan(point)

from scanprocessing.utils.ErrorsUtils import *
from scanprocessing.classes.Voxel import *
from scanprocessing.classes.VoxelLevels import *

from scanprocessing.classes.geometry.Point import *


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

    def __calc_vxl_md_bord(self):
        if len(self.scan) == 0:
            return None
        x0 = self.scan.borders["lower_left"].x // self.vxl_step * self.vxl_step
        y0 = self.scan.borders["lower_left"].y // self.vxl_step * self.vxl_step

        x_max = (self.scan.borders["upper_right"].x // self.vxl_step + 1) * self.vxl_step
        y_max = (self.scan.borders["upper_right"].y // self.vxl_step + 1) * self.vxl_step
        return {"lower_left": Point(x0, y0),
                "upper_left": Point(x0, y_max),
                "upper_right": Point(x_max, y_max),
                "lower_right": Point(x_max, y0)
                }

    def __create_vxl_struct(self):
        x_start = self.borders["lower_left"].x
        y_start = self.borders["lower_left"].y

        x_stop = self.borders["upper_right"].x
        y_stop = self.borders["upper_right"].y

        x_count = int((x_stop - x_start) / self.vxl_step)
        y_count = int((y_stop - y_start) / self.vxl_step)

        return [[Voxel(Point(x_start + x * self.vxl_step, y_start + y * self.vxl_step), self.vxl_lvl)
                 for x in range(x_count + 1)] for y in range(y_count + 1)]

    def __separate_scan_to_vxl(self):
        x_start = self.borders["lower_left"].x
        y_start = self.borders["lower_left"].y

        for point in self.scan.points:
            x, y = point.x, point.y
            vxl_md_X = int((x-x_start) // self.vxl_step)
            vxl_md_Y = int((y-y_start) // self.vxl_step)
            self.vxl_model[vxl_md_Y][vxl_md_X].scan.add_point_to_scan(point)

    def calc_vxl_planes(self):
        for vxl_row in self.vxl_model:
            for vxl in vxl_row:
                vxl.plane = Plane.fit_plane_to_point_arr(vxl.scan)
                vxl.update_vxl_z_borders()
                vxl.errors = ErrorsUtils(vxl)

        # На всякий случай
        # return {"lower_left": Voxel(Point(self.scan.borders["lower_left"].x // self.vxl_step * self.vxl_step,
        #                                   self.scan.borders["lower_left"].y // self.vxl_step * self.vxl_step),
        #                             self.vxl_lvl),
        #         "upper_left": Voxel(Point(self.scan.borders["upper_left"].x // self.vxl_step * self.vxl_step,
        #                                   self.scan.borders["upper_left"].y // self.vxl_step * self.vxl_step),
        #                             self.vxl_lvl),
        #         "upper_right": Voxel(Point(self.scan.borders["upper_right"].x // self.vxl_step * self.vxl_step,
        #                                    self.scan.borders["upper_right"].y // self.vxl_step * self.vxl_step),
        #                              self.vxl_lvl),
        #         "lower_right": Voxel(Point(self.scan.borders["lower_right"].x // self.vxl_step * self.vxl_step,
        #                                    self.scan.borders["lower_right"].y // self.vxl_step * self.vxl_step),
        #                              self.vxl_lvl)
        #         }

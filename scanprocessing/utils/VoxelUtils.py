import os.path
import pickle

import matplotlib.pyplot as plt

from scanprocessing.classes.VoxelModel import *
from scanprocessing.classes.Voxel import *


class VoxelUtils:

    @staticmethod
    def dump_vxl_mdl(vxl_mdl: VoxelModel):
        path = os.path.join(os.path.abspath(""), "saved_vxl_mdl", vxl_mdl.name + ".pkl_vxl_mdl")
        with open(path, "wb") as f:
            pickle.dump(vxl_mdl, f)

    @staticmethod
    def load_vxl_mdl(path):
        with open(path, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def plot_scan(vxl_mdl: VoxelModel):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        for vxl_row in vxl_mdl.vxl_model:
            for vxl in vxl_row:
                if vxl.plane is None:
                    continue

                x0 = vxl.vxl_borders["lower_left"].x
                y0 = vxl.vxl_borders["lower_left"].y
                step = vxl.voxel_level[0]
                x_max = vxl.vxl_borders["upper_right"].x + step
                y_max = vxl.vxl_borders["upper_right"].y + step

                a = vxl.plane.a
                b = vxl.plane.b
                d = vxl.plane.d

                X = np.arange(x0, x_max, step)
                Y = np.arange(y0, y_max, step)
                X, Y = np.meshgrid(X, Y)
                Z = a * X + b * Y + d

                ax.plot_surface(X, Y, Z, alpha=0.6)
        plt.show()

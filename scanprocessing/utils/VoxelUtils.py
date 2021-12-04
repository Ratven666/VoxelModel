import os.path
import pickle

import numpy as np
import matplotlib.pyplot as plt

# from scanprocessing.classes.VoxelModel import *
# from scanprocessing.classes.Voxel import *

from scanprocessing.classes import *


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

    @staticmethod
    def plot_errors(vxl_mdl: VoxelModel, name: str):
        x_list = []
        y_list = []

        for vxl_x_line in vxl_mdl.vxl_model[0]:
            x = (vxl_x_line.vxl_borders["lower_left"].x + vxl_x_line.vxl_borders["lower_right"].x) / 2
            x_list.append(x)
        for vxl_y_line in vxl_mdl.vxl_model:
            y = (vxl_y_line[0].vxl_borders["lower_left"].y + vxl_y_line[0].vxl_borders["upper_left"].y) / 2
            y_list.append(y)
        err = []
        for x in vxl_mdl.vxl_model:
            y_line = []
            for y in x:
                e = y.errors.errors[name]
                if e is None:
                    e = 0.0
                y_line.append(e)
            err.append(y_line[:-1])
        err = np.array(err[:-1])
        # err = np.array([[x.errors.errors[name] for x in y] for y in vxl_mdl.vxl_model])
        x_list.pop(-1)
        y_list.pop(-1)
        fig, ax = plt.subplots()
        im = ax.imshow(err)

        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel(f"Errors from {name}", rotation=-90, va="bottom")


        # We want to show all ticks...
        ax.set_xticks(np.arange(len(x_list)))
        ax.set_yticks(np.arange(len(y_list)))
        # ... and label them with the respective list entries
        ax.set_xticklabels(x_list)
        ax.set_yticklabels(y_list)

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")

        # Loop over data dimensions and create text annotations.
        for i in range(len(y_list)):
            for j in range(len(x_list)):
                text = ax.text(j, i, round(err[i, j], 1),
                               ha="center", va="center", color="w", fontsize="xx-small")

                # fontsize or size	float or {'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'}

        ax.set_title(f"Errors from {name}")
        fig.tight_layout()
        plt.show()


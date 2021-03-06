import os.path

import pickle
import matplotlib.pyplot as plt

from scanprocessing.classes.Scan import *


class ScanUtils:

    @staticmethod
    def parse_xyz_points_from_file(scan: Scan, path_to_file: str):
        with open(path_to_file, "r") as file:
            for line in file:
                # point = Point(*[float(lst) for lst in line.strip().split(" ")])
                point = Point(*[float(lst) * 3000 for lst in line.strip().split(" ")])
                scan.add_point_to_scan(point)

    @staticmethod
    def dump_scan(scan: Scan):
        path = os.path.join(os.path.abspath(""), "saved_scan", scan.name + ".pkl_scan")
        with open(path, "wb") as f:
            pickle.dump(scan, f)

    @staticmethod
    def load_scan(path):
        with open(path, "rb") as f:
            return pickle.load(f)

    @staticmethod
    def plot_3d_scan(scan: Scan, max_point_count=10_000):
        x_lst, y_lst, z_lst = [], [], []
        if len(scan) < max_point_count:
            step = 1
        else:
            step = int(len(scan) / max_point_count)
        for point in scan.points[::step]:
            x_lst.append(point.x)
            y_lst.append(point.y)
            z_lst.append(point.z)

        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
        ax.scatter(x_lst, y_lst, z_lst, marker="+")
        plt.show()

    @staticmethod
    def plot_2d_scan(scan: Scan, max_point_count=10_000):
        x_lst, y_lst = [], []
        if len(scan) < max_point_count:
            step = 1
        else:
            step = int(len(scan) / max_point_count)
        for point in scan.points[::step]:
            x_lst.append(point.x)
            y_lst.append(point.y)
        ax = plt.axes()
        ax.set_xlabel('x')                 #!!!!!!!!!!!!!!!!
        ax.set_ylabel('y')
        ax.scatter(x_lst, y_lst, marker=".", s=0.25, alpha=1)
        plt.show()

import os.path

import pickle
import matplotlib.pyplot as plt

from Point import *
from Scan import *

class ScanUtils:

    @staticmethod
    def parse_xyz_points_from_file(scan: Scan, path_to_file: str):
        with open(path_to_file, "r") as file:
            for line in file:
                point = Point(*[float(l) for l in line.strip().split(" ")])
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
    def plot_scan(scan: Scan, max_point_count=5_000):

        x_lst, y_lst, z_lst = [], [], []
        step = int(len(scan) / max_point_count)
        for point in scan.points[::step]:
            x_lst.append(point.x)
            y_lst.append(point.y)
            z_lst.append(point.z)

        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(x_lst, y_lst, z_lst, cmap=",")
        plt.show()

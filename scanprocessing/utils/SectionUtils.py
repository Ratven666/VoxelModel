import pickle
import matplotlib.pyplot as plt

from scanprocessing.classes.Section import *


class SectionUtils:

    @staticmethod
    def plot_2d_section(section: Section, max_point_count=10_000):
        ax = plt.axes()
        ax.set_xlabel('line')  # !!!!!!!!!!!!!!!!
        ax.set_ylabel('z')
        for sc in section.section_2d_scans:
            x_lst, y_lst = [], []
            if len(sc.points) < max_point_count:
                step = 1
            else:
                step = int(len(sc) / max_point_count)
            for point in sc.points[::step]:
                x_lst.append(point.x)
                y_lst.append(point.y)
            ax.scatter(x_lst, y_lst, marker=".", s=0.25, alpha=1)

            line = Line2D.fit_line_to_2d_scan(sc)
            x_st = 0
            x_ed = section.line.line_dist()
            y_st = -line.parameters["A"]*x_st - line.parameters["C"]
            y_ed = -line.parameters["A"]*x_ed - line.parameters["C"]
            ax.plot([x_st, x_ed], [y_st, y_ed])
            plt.show()

    @staticmethod
    def sep_section(section: Section, n: int):
        sec_lst = []
        step_line = section.line.line_dist() / n
        x_min = 0
        for sc in section.section_2d_scans:
            points = sc.points[:]
            for _ in range(n):
                x_max = x_min + step_line
                sec_lst.append([])
                for idx, point in enumerate(points):
                    if x_min < point.x <= x_max:
                        sec_lst[-1].append(points.pop(idx))
                    elif point.x > x_max:
                        x_min = x_max
                        break
        x_st = 0
        ax = plt.axes()
        ax.set_xlabel('line')  # !!!!!!!!!!!!!!!!
        ax.set_ylabel('z')
        for sec in sec_lst:
            x_lst, y_lst = [], []
            temp_sc = Scan("tmp")
            for point in sec:
                x_lst.append(point.x)
                y_lst.append(point.y)
                temp_sc.add_point_to_scan(point)
            ax.scatter(x_lst, y_lst, marker=".", s=0.2, alpha=0.5)
            if len(temp_sc) >= 2:
                line = Line2D.fit_line_to_2d_scan(temp_sc)
                x_ed = x_st + step_line
                y_st = -line.parameters["A"] * x_st - line.parameters["C"]
                y_ed = -line.parameters["A"] * x_ed - line.parameters["C"]
                ax.plot([x_st, x_ed], [y_st, y_ed])
            x_st = x_ed
        plt.show()







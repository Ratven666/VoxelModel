from os import remove

from DB_StripScan import *

class Section:

    def __init__(self, line2D: Line2D, width: (int, float), scan: Scan):
        self.line2D = line2D
        self.width = width
        self.scan = scan
        self.strip_scan = StripScan.cut_scan(line2D, width, scan)
        self.section_2d_scan = self.__calk_2d_projection()
        self.sec_scans = {}
        self.line_list = {}

    def __len__(self):
        return len(self.section_2d_scan)

    def __iter__(self):
        """Возвращает итератор последовательно выдающий объеты Point для всех точек скана""" #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return iter(Scan2dIterator(self.section_2d_scan))

    def __str__(self):
        return f"SECTION_{str(self.strip_scan)}"

    def __repr__(self):
        return self.__str__()

    def __calk_2d_projection(self):
        x0 = self.line2D.start_point.x
        y0 = self.line2D.start_point.y
        temp_scan = Scan(Project(""), f"2D_{self.strip_scan.name}")
        file_name = f"{self.__str__()}_2D.txt"
        with open(file_name, "w") as file:
            for point in self.strip_scan:
                p_x = point.x
                p_y = point.y
                p_normal = point.normal
                p_color = point.color
                x = ((x0-p_x)**2 + (y0-p_y)**2) ** 0.5
                y = point.z
                if None not in p_color and None not in p_normal:
                    data = f"{x} {y} {0} " \
                           f"{p_color[0]} {p_color[1]} {p_color[2]} " \
                           f"{p_normal[0]} {p_normal[1]} {p_normal[2]}\n"
                elif None not in p_color:
                    data = f"{x} {y} {0} {p_color[0]} {p_color[1]} {p_color[2]}\n"
                else:
                    data = f"{x} {y} {0}\n"
                file.write(data)
        temp_scan.parse_points_from_file(file_name)
        remove(file_name)
        return temp_scan

    def sep_section(self, n: int):
        if n not in self.sec_scans:
            self.sec_scans[n] = [Scan(Project(""), f"SC_sec_w{self.width}_n{n}_{idx}") for idx in range(n)]
            scans_id = [scan.scan_id for scan in self.sec_scans[n]]
            step_line = self.line2D.line_dist() / n
            data = []
            for point in self.section_2d_scan:
                sec_idx_X = int(point.x // step_line)
                try:
                    data.append((point.point_id, scans_id[sec_idx_X]))
                except IndexError:
                    pass
            with Project("") as project:
                project.executemany("INSERT OR IGNORE INTO points_scans (point_id, scan_id) VALUES (?, ?)", data)
            [scan.calc_scan_metrics() for scan in self.sec_scans[n]]
            [scan.update_scan_metrics_in_db() for scan in self.sec_scans[n]]
            self.__fit_lines_in_sections(n)
            self.__calc_lines_statistics(n)

    def __fit_lines_in_sections(self, n):
        self.line_list[n] = [Line2D.fit_line_to_2d_scan(scan) for scan in self.sec_scans[n]]

    def __calc_lines_statistics(self, n):
        vv = 0
        vv_line = 0
        data = f"№\tk\tb\tPoints_count\tMSE\tMSE_line\tR2\n"
        for idx, scan in enumerate(self.sec_scans[n]):
            with Project("") as project:
                y_avg = project. execute("""SELECT AVG(p.Y) 
                            FROM points p
                            JOIN points_scans ps ON ps.point_id = p.id
                            WHERE ps.scan_id = (?)""", (scan.scan_id,)).fetchone()[0]
            line = self.line_list[n][idx]
            for point in scan:
                y_line = -line.parameters["A"] * point.x - line.parameters["C"]
                vv += (point.y - y_avg) ** 2
                vv_line += (point.y - y_line) ** 2
            mse = (vv / (len(scan) - 1)) ** 0.5
            mse_line = (vv_line / (len(scan) - 2)) ** 0.5
            R2 = 1 - (mse_line ** 2) / (mse **2)
            data += f"{idx+1}\t{round(-line.parameters['A'], 5)}\t{round(-line.parameters['C'], 5)}\t" \
                    f"{len(scan)}\t{round(mse, 5)}\t{round(mse_line, 5)}\t{round(R2, 5)}\n"
        with open(f"LineStat_{self.scan.__str__()}_width{self.width}_n{n}.txt", "w") as file:
            file.write(data)

    def plot_section(self, n, true_scale=True):
        x_st = 0
        ax = plt.axes()
        ax.set_xlabel('line')  # !!!!!!!!!!!!!!!!
        ax.set_ylabel('z')
        if true_scale is True:
            self.__plot_limits(ax)
        step_line = self.line2D.line_dist() / n
        for idx, scan in enumerate(self.sec_scans[n]):
            x_lst, y_lst, c_lst = [], [], []
            for point in scan:
                x_lst.append(point.x)
                y_lst.append(point.y)

                if point.color == (None, None, None):
                    c_lst.append((0, 0, 0))
                else:
                    c_lst.append([el / 255.0 for el in point.color])

            ax.scatter(x_lst, y_lst, c=c_lst, marker=".", s=0.5, alpha=0.1)
            if self.line_list[n][idx] is not None:
                line = self.line_list[n][idx]
                x_ed = x_st + step_line
                y_st = -line.parameters["A"] * x_st - line.parameters["C"]
                y_ed = -line.parameters["A"] * x_ed - line.parameters["C"]
                ax.plot([x_st, x_ed], [y_st, y_ed])
            x_st = x_ed
        ax.grid(True)
        plt.show()

    def plot(self, max_point_count=10_000, true_scale=True):
        x_lst, y_lst, c_lst = [], [], []
        if len(self) < max_point_count:
            step = 1
        else:
            step = int(len(self) / max_point_count)
        count = 0
        for point in self.section_2d_scan:
            if count == 0:
                x_lst.append(point.x)
                y_lst.append(point.y)

                if point.color == (None, None, None):
                    c_lst.append((0, 0, 0))
                else:
                    c_lst.append([el / 255.0 for el in point.color])
            count += 1
            if count == step:
                count = 0

        px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
        fig = plt.figure(figsize=(800 * px, 800 * px))
        ax = fig.add_subplot()

        if true_scale is True:
            self.__plot_limits(ax)

        ax.scatter(x_lst, y_lst, c=c_lst, marker="+", s=2)
        ax.grid(True)
        plt.show()

    def __plot_limits(self, ax):
        min_x, min_y = self.section_2d_scan.borders["min_X"], self.section_2d_scan.borders["min_Y"]
        max_x, max_y = self.section_2d_scan.borders["max_X"], self.section_2d_scan.borders["max_Y"]
        limits = [max_x - min_x,
                  max_y - min_y]
        length = max(limits) / 2
        x_lim = [((min_x + max_x)/2) - length, ((min_x + max_x)/2) + length]
        y_lim = [((min_y + max_y)/2) - length, ((min_y + max_y)/2) + length]
        ax.set_xlim(*x_lim)
        ax.set_ylim(*y_lim)


class Scan2dIterator:

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
                                                    WHERE ps.scan_id = (?) ORDER BY p.X""", (self.scan_id,)))
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
    pr = Project("Line")

    sc15 = Scan(pr, "Kucha")

    sc15.parse_points_from_file(os.path.join("src", "KuchaRGB.txt"))

    # sc15.plot()

    p1 = Point(-4, -23)
    p2 = Point(-4, -0.4)

    line = Line2D(p1, p2)

    sec = Section(line, 1, sc15)
    # #
    # str_sc15_2 = StripScan.cut_scan(line, 2, sc15)
    # str_sc15_1 = StripScan.cut_scan(line, 1, sc15)
    # str_sc15_3 = StripScan(pr, line, 3)
    # str_sc15_3.parse_points_from_file(os.path.join("src", "KuchaRGB.txt"))

    # str_sc15_1.plot()

    print(line)

    sec.section_2d_scan.plot(true_scale=True)


from scanprocessing.classes.StripScan import *
from scanprocessing.classes.geometry.Line2D import *

import scanprocessing as sp


class Section:

    def __init__(self, line: Line2D, width: (int, float), *scan: Scan):
        self.line = line
        self.width = width
        self.scans = list(scan)
        self.section_scans = [self.__calk_line_scan(sc) for sc in self.scans]
        self.section_2d_scans = [self.__calk_2d_projection(sc) for sc in self.section_scans]

    def __str__(self):
        return str(self.scans)

    def __calk_line_scan(self, sc: Scan):
        temp_scan = Scan(f"SECTION_{scan.name}")
        for point in sc.points:
            if self.line.distance_from_point_to_line(point) <= self.width:
                point = self.line.calk_point_on_line(point)
                if isinstance(point, Point):
                    temp_scan.add_point_to_scan(point)
        return temp_scan

    def __calk_2d_projection(self, line_scan: Scan):
        x0 = self.line.start_point.x
        y0 = self.line.start_point.y
        temp_scan = Scan(f"2D_{scan.name}")
        for point in line_scan.points:
            p_x = point.x
            p_y = point.y
            x = ((x0-p_x)**2 + (y0-p_y)**2) ** 0.5
            y = point.z
            temp_scan.add_point_to_scan(Point(x, y))
        temp_scan.points.sort(key=lambda pt: pt.x)
        return temp_scan


if __name__ == "__main__":
    scan = sp.ScanUtils.load_scan("D:\\VoxelModel\\saved_scan\\15_sandbox.pkl_scan")

    p1 = sp.Point(250, 920)
    p2 = sp.Point(1100, -120)

    # p1 = sp.Point(490, 650)
    # p2 = sp.Point(700, 200)

    l1 = sp.Line2D(p1, p2)
    print(l1)

    sec = Section(l1, 5, scan)

    # for scan in sec.section_scans:
    #     sp.ScanUtils.plot_3d_scan(scan)

    # sp.SectionUtils.plot_2d_section(sec)

    sp.SectionUtils.sep_section(sec, 10)

    # for scan in sec.section_2d_scans:
    #     print(len(scan))
    #     print(sec.line.fit_line_to_2d_scan(scan))
    #     sp.ScanUtils.plot_2d_scan(scan)



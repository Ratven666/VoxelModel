from Scan import *
from Point import *
from ScanUtils import *

p1 = Point(1.2, 2.2, 3.4)
p2 = Point(2, 4, 5)
scan1 = Scan("15_yash")

print(len(scan1))

# ScanUtils.parse_xyz_points_from_file(scan1, "src\\15.txt")

# ScanUtils.dump_scan(scan1)

scan2 = ScanUtils.load_scan("saved_scan\\15_yash.pkl_scan")

p1 = Point(1.2, 2.2, 3.4)
print(p1)

print(len(scan1))

ScanUtils.plot_scan(scan2)
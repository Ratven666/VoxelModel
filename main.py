from scanprocessing.utils.ScanUtils import *
from scanprocessing.classes.VoxelModel import *

p1 = Point(1.2, 2.2, 3.4)
p2 = Point(2, 4, 5)
scan1 = Scan("15_yash")


# ScanUtils.parse_xyz_points_from_file(scan1, "src\\15.txt")
#
# ScanUtils.dump_scan(scan1)

scan2 = ScanUtils.load_scan("saved_scan\\15_yash.pkl_scan")

print(scan2)



# ScanUtils.plot_scan(scan2)

vxl_md = VoxelModel(scan2)

print(vxl_md)
print(len(vxl_md))
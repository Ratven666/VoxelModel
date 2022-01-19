from DB_Section import *
from DB_VoxelModel import *

pr = Project("Karier")
#
sc = Scan(pr, "Karier")
#
sc.parse_points_from_file(os.path.join("src", "Karier.txt"))

# sc.plot(max_point_count=30000)
#
# vm = VoxelModel(sc, 10)
# vm.fit_planes_in_vxl()
# #
# vm.plot()
# #
p1 = Point(16495242, 6638571)
p2 = Point(16495243, 6638970)
#
p3 = Point(0.07, 0.03)
p4 = Point(0.03, -0.07)
# #
line = Line2D(p1, p2)
line2 = Line2D(p3, p4)
# #
sec = Section(line, 20, sc)
# sec2 = Section(line2, 0.02, sc)
# #
sec.strip_scan.plot(true_scale=True)
sec.section_2d_scan.plot(true_scale=True)
sec.plot(true_scale=True)

# sec2.strip_scan.plot(true_scale=True)
# sec2.section_2d_scan.plot(true_scale=True)
# sec2.plot(true_scale=True)

# # import numpy as np
# import scipy
# from scipy.spatial import ConvexHull
#
# # points = np.array([[0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0], [1, 1, 1], [1, 0, 1], [0, 0, 0]])  # your points
# volume = scipy.spatial.ConvexHull([[0, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 0]]).volume
# #
# # points = np.array([[0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0], [1, 1, 1], [1, 0, 1], [0, 0, 0]])  # your points
# # volume = scipy.spatial.ConvexHull(points).volume
#
# print(volume)

import sqlite3

from  DB_VoxelModel import *

pr = Project("test")

sc1 = Scan(pr, "test")

sc1.parse_points_from_file(os.path.join("src", "15_1248.txt"))

# sc1.plot()

vm = VoxelModel(sc1, 0.05)
vm.fit_planes_in_vxl()

# vm.plot()

with pr as p:
    ids = (2391, 2392)
    st = "(?), (?)"
    # print(st)
    #
    st1 = '(?), ' * len(ids)
    st1 = st1[:-2]
    print(bytes(st, "utf-8"))
    print(bytes(st1, "utf-8"))
    # data = p.execute(f"""SELECT count(*) FROM points p
    #                       JOIN points_scans ps ON ps.point_id = p.id
    #                       WHERE ps.scan_id in ((?), (?))""", ids).fetchall()
    #
    data = p.execute(f"""SELECT * FROM points p
                          JOIN points_scans ps ON ps.point_id = p.id
                          WHERE ps.scan_id in ({st1.strip()}) ORDER BY scan_id""", ids).fetchall()

    print(len(Scan.get_scan_from_id(2391)))

# for el in data[:len(Scan.get_scan_from_id(2391))]:
#     print(el)

for el in data:
    if el[-1] == 2391:
        print(el)
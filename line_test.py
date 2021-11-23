import scanprocessing as sp

p1 = sp.Point(250, 1150)
p2 = sp.Point(935, -290)

p1 = sp.Point(500, 0)
# p2 = sp.Point(501, 1000)

l1 = sp.Line2D(p1, p2)

print(l1.parameters)
print(l1)



scan = sp.StripScan(l1, 20)
# scan = sp.Scan("123")

# scan.add_point_to_scan(sp.Point(500, 500))

sp.ScanUtils.parse_xyz_points_from_file(scan, "src\\15.txt")

print(scan)

sp.ScanUtils.plot_3d_scan(scan)

vxl_md = sp.VoxelModel(scan, vxl_lvl=sp.VoxelLevels.LEVELS["level_5"])


print(vxl_md)

vxl_md.calc_vxl_planes()

sp.VoxelUtils.plot_scan(vxl_md)

sp.VoxelUtils.plot_errors(vxl_md, "z_mse")
sp.VoxelUtils.plot_errors(vxl_md, "dist_mse")


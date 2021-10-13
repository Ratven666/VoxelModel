import scanprocessing as sp


scan = sp.Scan("15_sandbox")

# sp.ScanUtils.parse_xyz_points_from_file(scan, "src\\15.txt")
#
# sp.ScanUtils.dump_scan(scan)

scan = sp.ScanUtils.load_scan("saved_scan\\15_sandbox.pkl_scan")

# sp.ScanUtils.plot_scan(scan)

print(scan)
#
vxl_md = sp.VoxelModel(scan, vxl_lvl=sp.VoxelLevels.LEVELS["level_4"])


print(vxl_md)

vxl_md.calc_vxl_planes()

sp.VoxelUtils.plot_scan(vxl_md)

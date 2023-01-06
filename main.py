from DB_VoxelModel import *


pr = Project("Kucha_2")
sc1 = Scan(pr, "Kucha_2")
sc1.parse_points_from_file("src\Kucha_2.txt")


# sc1.plot(max_point_count=50_000)


vm = VoxelModel(sc1, 1)
vm.fit_planes_in_vxl(force_fit=False)

# for vxl in vm:
#     if vxl.mse_plane is not None:
#         print(vxl.id, vxl.mse_z, vxl.mse_plane)


# vm.plot(true_scale=True, alpha=1)
vm.plot_3d_dem(true_scale=True, alpha=1)
vm.plot_2d_map("mse_plane", print_legend=False, border_val=(0, 0.5))
vm.plot_2d_map("mse_dem", print_legend=False, border_val=(0, 0.8))
vm.plot_2d_map("len", print_legend=False, border_val=(0, 900))
vm.plot_2d_map("R^2", print_legend=False, border_val=(0, 1))
print()


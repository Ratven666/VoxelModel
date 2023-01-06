from os import remove

import matplotlib.pyplot as plt

from DB_Voxel import *


class VoxelModel:

    def __init__(self, scan: Scan, step):
        self.name = f"VM_Sc:{scan.name}_st:{step}"
        self.base_scan = scan
        self.step = step
        self.borders = self.__calc_vxl_md_bord()
        self.vxl_model = None
        self.vxl_mdl_id = self.__init_vxl_mdl()

    def __len__(self):
        return len(self.vxl_model) * len(self.vxl_model[0])

    def __iter__(self):
        return VoxelModelIterator(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __init_vxl_mdl(self):
        with Project("") as project:
            vxl_mdl_data = project.execute("""SELECT vm.id, vm.name, vm.step, vm.min_X,
                                                vm.max_X, vm.min_Y, vm.max_Y, vm.base_scan_id
                                                FROM voxels_model vm WHERE vm.name = (?)""", (self.name,)).fetchone()
        if vxl_mdl_data is None or len(vxl_mdl_data) == 0:
            with Project("") as project:
                vxl_mdl_id = project.execute("""INSERT INTO voxels_model (name, step, min_X, max_X, 
                                                                    min_Y, max_Y, base_scan_id) 
                                                                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                                                            (self.name,
                                                                             self.step,
                                                                             self.borders["min_X"],
                                                                             self.borders["max_X"],
                                                                             self.borders["min_Y"],
                                                                             self.borders["max_Y"],
                                                                             self.base_scan.scan_id)).lastrowid
            self.vxl_model = self.__create_vxl_struct(vxl_mdl_id)
            self.__separate_scan_to_vxl()
            return vxl_mdl_id
        vxl_mdl_id = vxl_mdl_data[0]
        self.vxl_model = self.__create_vxl_struct(vxl_mdl_id)
        # self.__separate_scan_to_vxl()
        return vxl_mdl_id

    def __calc_vxl_md_bord(self):
        if len(self.base_scan) == 0:
            return None
        x0 = self.base_scan.borders["min_X"] // self.step * self.step
        y0 = self.base_scan.borders["min_Y"] // self.step * self.step

        x_max = (self.base_scan.borders["max_X"] // self.step + 1) * self.step
        y_max = (self.base_scan.borders["max_Y"] // self.step + 1) * self.step
        return {"min_X": x0,
                "max_X": x_max,
                "min_Y": y0,
                "max_Y": y_max}

    def __create_vxl_struct(self, vxl_mdl_id):
        x_start = self.borders["min_X"]
        y_start = self.borders["min_Y"]

        x_stop = self.borders["max_X"]
        y_stop = self.borders["max_Y"]

        x_count = int((x_stop - x_start) / self.step)
        y_count = int((y_stop - y_start) / self.step)

        return [[Voxel(Point(x_start + x * self.step, y_start + y * self.step), self.step, vxl_mdl_id)
                 for x in range(x_count)] for y in range(y_count)]

    def __separate_scan_to_vxl(self):
        x_start = self.borders["min_X"]
        y_start = self.borders["min_Y"]

        with open("temp_file.txt", "w") as file:
            for point in self.base_scan:
                x, y = point.x, point.y
                vxl_md_X = int((x - x_start) // self.step)
                vxl_md_Y = int((y - y_start) // self.step)
                scan = self.vxl_model[vxl_md_Y][vxl_md_X].scan
                scan.len += 1
                scan.update_borders(point)
                file.write(f"{point.point_id}, {scan.scan_id}\n")
        point_n = 100000
        id_point_scan = []
        with Project("") as project:
            with open("temp_file.txt", "r") as file:
                for line in file:
                    data = [int(p_ps) for p_ps in line.strip().split(",")]
                    id_point_scan.append(tuple(data))
                    if len(id_point_scan) == point_n:
                        project.executemany("INSERT OR IGNORE INTO points_scans (point_id, scan_id) VALUES (?, ?)",
                                            id_point_scan)
                        id_point_scan = []
                try:
                    project.executemany("INSERT OR IGNORE INTO points_scans (point_id, scan_id) VALUES (?, ?)",
                                                id_point_scan)
                except sqlite3.OperationalError:
                    pass
        remove("temp_file.txt")
        for voxel in self:
            voxel.scan.update_scan_metrics_in_db()

    def fit_planes_in_vxl(self, force_fit=False):
        for voxel in self:
            if voxel.scan.len == 0:
                print(f"Empty vxl:{voxel.id}")
                continue
            if voxel.avg_z is not None and voxel.mse_z is not None and \
                        voxel.mse_plane is not None and force_fit is False:
                print(f"Ready vxl:{voxel.id} (len={voxel.scan.len})")
                continue

            xyz_rgb = np.array([[point.x, point.y, point.z,
                                 point.color[0], point.color[1], point.color[2]] for point in voxel.scan])

            voxel.plane.fit_plane_to_np_xyz_rgb(xyz_rgb, force_fit)
            voxel._calk_mse_from_np_xyz_rgb(xyz_rgb, force_fit)
            print(f"\tCalk vxl:{voxel.id} (len={len(xyz_rgb)})")

    def plot(self, true_scale=True, alpha=0.6):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        if true_scale is True:
            self.base_scan._Scan__plot_limits(ax)

        for voxel in self:
            plane = voxel.plane
            if plane.is_calculated() is False:
                continue

            x0 = voxel.vxl_borders["lower_left"].x
            y0 = voxel.vxl_borders["lower_left"].y
            step = voxel.step
            x_max = voxel.vxl_borders["upper_right"].x + step
            y_max = voxel.vxl_borders["upper_right"].y + step

            a = plane.a
            b = plane.b
            d = plane.d

            X = np.arange(x0, x_max, step)
            Y = np.arange(y0, y_max, step)
            X, Y = np.meshgrid(X, Y)
            Z = a * X + b * Y + d

            if plane.color == (None, None, None):
                c_lst = (0, 0, 0)
            else:
                c_lst = [el / 255.0 for el in plane.color]

            ax.plot_surface(X, Y, Z, color=c_lst, alpha=alpha)
        plt.show()

    def plot_3d_dem(self, true_scale=True, alpha=0.6):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        if true_scale is True:
            self.base_scan._Scan__plot_limits(ax)

        for voxel in self:
            plane = voxel.plane
            if plane.is_calculated() is False:
                continue

            if voxel.avg_z is None:
                continue

            x0 = voxel.vxl_borders["lower_left"].x
            y0 = voxel.vxl_borders["lower_left"].y
            step = voxel.step
            x_max = voxel.vxl_borders["upper_right"].x + step
            y_max = voxel.vxl_borders["upper_right"].y + step

            X = np.arange(x0, x_max, step)
            Y = np.arange(y0, y_max, step)
            X, Y = np.meshgrid(X, Y)
            Z = 0 * X + 0 * Y + voxel.avg_z

            if plane.color == (None, None, None):
                c_lst = (0, 0, 0)
            else:
                c_lst = [el / 255.0 for el in plane.color]

            ax.plot_surface(X, Y, Z, color=c_lst, alpha=alpha)
        plt.show()

    def plot_2d_map(self, name="mse_plane", print_legend=True, border_val=(0, 1)):
        x_list = []
        y_list = []

        for vxl_x_line in self.vxl_model[0]:
            x = (vxl_x_line.vxl_borders["lower_left"].x + vxl_x_line.vxl_borders["lower_right"].x) / 2
            x_list.append(x)
        for vxl_y_line in self.vxl_model:
            y = (vxl_y_line[0].vxl_borders["lower_left"].y + vxl_y_line[0].vxl_borders["upper_left"].y) / 2
            y_list.append(y)
        err = []
        for x in self.vxl_model:
            y_line = []
            for y in x:
                if name == "mse_plane":
                    e = y.mse_plane
                    e = self.__filtered_mse(y.mse_plane, border_val)
                elif name == "mse_dem":
                    # e = y.mse_z
                    e = self.__filtered_mse(y.mse_z, border_val)
                elif name == "len":
                    # e = y.scan.len
                    e = y.scan.len
                    e = self.__filtered_mse(y.scan.len, border_val)
                elif name == "R^2":
                    # e = y.calk_r2()
                    e = e = self.__filtered_mse(y.calk_r2(), border_val)
                elif name == "2d_dem":
                    # e = y.avg_z
                    e = self.__filtered_mse(y.avg_z, border_val)
                else:
                    raise ValueError("Нет такого типа данных!")
                if e is None:
                    e = 0.0
                y_line.append(e)
            err.append(y_line[:])
        err = np.array(err[::-1])

        fig, ax = plt.subplots()
        # im = ax.imshow(err, cmap="rainbow")
        im = ax.imshow(err, cmap="jet")

        cbar = ax.figure.colorbar(im, ax=ax)
        # cbar.ax.set_ylabel(f"Errors from {name}", rotation=-90, va="bottom")
        cbar.ax.set_ylabel(f"Map of {name} from {self.name}", rotation=-90, va="bottom")


        # We want to show all ticks...
        ax.set_xticks(np.arange(len(x_list)))
        ax.set_yticks(np.arange(len(y_list)))
        # ... and label them with the respective list entries
        ax.set_xticklabels(x_list[::])
        ax.set_yticklabels(y_list[::-1])

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")

        # Loop over data dimensions and create text annotations.
        if print_legend is True:
            for i in range(len(y_list)):
                for j in range(len(x_list)):
                    text = ax.text(j, i, round(err[i, j], 3),
                                   ha="center", va="center", color="w", fontsize="xx-small")

                # fontsize or size	float or {'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'}

        ax.set_title(f"Map of {name} from {self.name}")
        fig.tight_layout()
        plt.show()

    def __filtered_mse(self, value, border_val=100_000):
        try:
            if value is None:
                value = 0
            if value > border_val[1]:
                return border_val[1]
            elif value < border_val[0]:
                return border_val[0]
            else:
                return value
        except:
            return value

    def volume_calculation(self, base_lvl=0):
        total_volume = 0
        for voxel in self:
            total_volume += voxel.vxl_volume(base_lvl)
        return total_volume

    # def __separate_scan_to_vxl(self):
    #     x_start = self.borders["min_X"]
    #     y_start = self.borders["min_Y"]
    #
        # connection = self.base_scan.project.sqlite_connection
        # cursor_inn = connection.cursor()
    #     try:
    #         point_n = 100000
    #         id_point_scan = []
    #         for point in self.base_scan:
    #             x, y = point.x, point.y
    #             vxl_md_X = int((x - x_start) // self.step)
    #             vxl_md_Y = int((y - y_start) // self.step)
    #             scan = self.vxl_model[vxl_md_Y][vxl_md_X].scan
    #             id_point_scan.append((point.point_id, scan.scan_id))
    #             if len(id_point_scan) == point_n:
    #                 print("100_000!!!")
    #                 cursor_inn.executemany("INSERT INTO points_scans (point_id, scan_id) VALUES (?, ?)",
    #                                                                             id_point_scan)
    #                 print("!!!")
    #                 id_point_scan = []
    #         try:
    #             cursor_inn.executemany("INSERT INTO points_scans (point_id, scan_id) VALUES (?, ?)",
    #                                                                             id_point_scan)
    #         except sqlite3.OperationalError:
    #             pass
    #     finally:
    #         connection.commit()
    #         cursor_inn.close()
    #         print("LOL")
    #     print("sep end")
    #     for vxl_row in self.vxl_model:
    #         for vxl in vxl_row:
    #             vxl.scan.calc_scan_metrics()
    #             vxl.scan.update_scan_metrics_in_db()

        #         for line in file:
        #             data = [int(p_ps) for p_ps in line.strip().split(",")]
        #             id_point_scan.append(tuple(data))
        #             if len(id_point_scan) == point_n:
        #                 project.executemany("INSERT INTO points_scans (point_id, scan_id) VALUES (?, ?)",
        #                                     id_point_scan)
        #                 id_point_scan = []
        #         try:
        #             project.executemany("INSERT INTO points_scans (point_id, scan_id) VALUES (?, ?)",
        #                                 id_point_scan)
        #         except sqlite3.OperationalError:
        #             pass
        #
        #
        # for point in self.base_scan:
        #     x, y = point.x, point.y
        #     vxl_md_X = int((x - x_start) // self.step)
        #     vxl_md_Y = int((y - y_start) // self.step)
        #     scan = self.vxl_model[vxl_md_Y][vxl_md_X].scan
        #     cursor_inn.execute("INSERT OR IGNORE INTO points_scans (point_id, scan_id) VALUES (?, ?)",
        #                                                      (point.point_id, scan.scan_id))
        #
        # connection.commit()
        # cursor_inn.close()
        # for vxl_row in self.vxl_model:
        #     for vxl in vxl_row:
        #         vxl.scan.calc_scan_metrics()
        #         vxl.scan.update_scan_metrics_in_db()

    # def calc_vxl_planes(self):
    #     for vxl_row in self.vxl_model:
    #         for vxl in vxl_row:
    #             vxl.plane = Plane.fit_plane_to_scan(vxl.scan)
    #             vxl.update_vxl_z_borders()
    #             vxl.errors = ErrorsUtils(vxl)

class VoxelModelIterator:

    def __init__(self, vxl_mdl: VoxelModel):
        self.vxl_mdl = vxl_mdl
        self.i = 0
        self.j = 0
        self.len_i = len(vxl_mdl.vxl_model)
        self.len_j = len(vxl_mdl.vxl_model[0])

    def __iter__(self):
        return self

    def __next__(self):
        for vxl_col in range(self.i, self.len_i):
            for vxl_row in range(self.j, self.len_j):
                self.j += 1
                return self.vxl_mdl.vxl_model[vxl_col][vxl_row]
            self.i += 1
            self.j = 0
        raise StopIteration


if __name__ == "__main__":
    import time
    pr = Project("Balakovo")
    # t0 = time.time()
    sc1 = Scan(pr, "Balakovo")
    # print(time.time() - t0)
    # t0 = time.time()
    sc1.parse_points_from_file(os.path.join("src", "Balakovo.txt"))
    #
    # sc1.plot()
    # print(time.time() - t0)
    # t0 = time.time()

    # vm = VoxelModel(sc1, 2.5)
    # vm = VoxelModel(sc1, 25)
    #
    # # print(time.time() - t0)
    # # t0 = time.time()
    # vm.fit_planes_in_vxl(force_fit=False)
    # # print(time.time() - t0)



    # vm = VoxelModel(sc1, 50)
    # # vm.fit_planes_in_vxl(force_fit=False)
    # vm.plot(true_scale=True, alpha=1)
    # vm.plot_3d_dem(true_scale=True, alpha=1)
    #
    # vm.plot_2d_map("2d_dem", print_legend=False, border_val=(20, 150))
    # vm.plot_2d_map("mse_plane", print_legend=False, border_val=(0, 2))
    # vm.plot_2d_map("mse_dem", print_legend=False, border_val=(0, 5))
    # vm.plot_2d_map("len", print_legend=False, border_val=(20_000, 70_000))
    # vm.plot_2d_map("R^2", print_legend=False, border_val=(0, 1))
    # vm.plot_2d_map("R^2", print_legend=False, border_val=(0.3, 0.7))

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!25!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # vm = VoxelModel(sc1, 25)
    # # vm.fit_planes_in_vxl(force_fit=False)
    # vm.plot(true_scale=True, alpha=1)
    # vm.plot_3d_dem(true_scale=True, alpha=1)
    #
    # vm.plot_2d_map("2d_dem", print_legend=False, border_val=(20, 150))
    # vm.plot_2d_map("mse_plane", print_legend=False, border_val=(0, 2))
    # vm.plot_2d_map("mse_dem", print_legend=False, border_val=(0, 5))
    # vm.plot_2d_map("len", print_legend=False, border_val=(20_000, 70_000))
    # vm.plot_2d_map("R^2", print_legend=False, border_val=(0, 1))
    # vm.plot_2d_map("R^2", print_legend=False, border_val=(0.3, 0.7))




    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 10 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    vm = VoxelModel(sc1, 10)
    # vm.fit_planes_in_vxl(force_fit=False)
    vm.plot(true_scale=True, alpha=1)
    vm.plot_3d_dem(true_scale=True, alpha=1)
    vm.plot_2d_map("2d_dem", print_legend=False, border_val=(20, 150))
    vm.plot_2d_map("mse_plane", print_legend=False, border_val=(0, 0.6))
    vm.plot_2d_map("mse_dem", print_legend=False, border_val=(0, 3))
    vm.plot_2d_map("len", print_legend=False, border_val=(5_000, 15_000))
    vm.plot_2d_map("R^2", print_legend=False, border_val=(0, 1))
    vm.plot_2d_map("R^2", print_legend=False, border_val=(0.3, 0.7))

    # t0 = time.time()
    # print("vol", vm.volume_calculation(base_lvl=33))
    # print(time.time() - t0)
    # # sc1.plot()

    # vm = VoxelModel(sc1, 25)
    # # vm.fit_planes_in_vxl(force_fit=False)
    # vm.plot(true_scale=True, alpha=1)
    # vm.plot_3d_dem(true_scale=True, alpha=1)
    #
    # vm.plot_2d_map("2d_dem", print_legend=False, border_val=(20, 150))
    # vm.plot_2d_map("mse_plane", print_legend=False, border_val=(0, 2))
    # vm.plot_2d_map("mse_dem", print_legend=False, border_val=(0, 5))
    # vm.plot_2d_map("len", print_legend=False, border_val=(20_000, 70_000))
    # vm.plot_2d_map("R^2", print_legend=False, border_val=(0, 1))
    # vm.plot_2d_map("R^2", print_legend=False, border_val=(0.3, 0.7))

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 10 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # vm = VoxelModel(sc1, 10)
    # # vm.fit_planes_in_vxl(force_fit=False)
    # vm.plot(true_scale=True, alpha=1)
    # vm.plot_3d_dem(true_scale=True, alpha=1)
    # vm.plot_2d_map("2d_dem", print_legend=False, border_val=(20, 150))
    # vm.plot_2d_map("mse_plane", print_legend=False, border_val=(0, 0.6))
    # vm.plot_2d_map("mse_dem", print_legend=False, border_val=(0, 3))
    # vm.plot_2d_map("len", print_legend=False, border_val=(5_000, 15_000))
    # vm.plot_2d_map("R^2", print_legend=False, border_val=(0, 1))
    # vm.plot_2d_map("R^2", print_legend=False, border_val=(0.3, 0.7))

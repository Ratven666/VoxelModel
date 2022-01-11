from os import remove

from DB_Voxel import *


class VoxelModel:

    def __init__(self, scan: Scan, step):
        self.name = f"VM_Sc:{scan.name}_st:{step}"
        self.base_scan = scan
        self.step = step
        self.borders = self.__calc_vxl_md_bord()
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

    # def __separate_scan_to_vxl(self):
    #     x_start = self.borders["min_X"]
    #     y_start = self.borders["min_Y"]
    #
    #     connection = self.base_scan.project.sqlite_connection
    #     cursor_inn = connection.cursor()
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
    pr = Project("15")
    t0 = time.time()
    sc1 = Scan(pr, "15")
    print(time.time() - t0)
    t0 = time.time()
    sc1.parse_points_from_file(os.path.join("src", "15.txt"))
    print(time.time() - t0)
    t0 = time.time()
    vm = VoxelModel(sc1, 0.1)
    print(time.time() - t0)
    t0 = time.time()

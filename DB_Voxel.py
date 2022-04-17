from scipy.spatial import ConvexHull

from DB_Plane import *


class Voxel:

    def __init__(self, lower_left_point: Point, step: float, vxl_mdl_id):
        self.lower_left_point = lower_left_point
        self.step = step
        self.vxl_mdl_id = vxl_mdl_id
        self.name = f"VXL_VM{self.vxl_mdl_id}_s{self.step}_" \
                    f"X{round(self.lower_left_point.x, 5)}_" \
                    f"Y{round(self.lower_left_point.y, 5)}"
        self.scan = Scan(Project(""), f"SC_{self.name}")
        self.avg_z = None
        self.mse_z = None
        self.mse_plane = None
        self.id = self.__init_voxel()
        self.vxl_borders = self.__calk_voxel_borders()
        # self.errors = None
        #
        # self.sub_voxel_model = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @property
    def plane(self):
        return Plane(self.plane_id)

    def __init_voxel(self):
        with Project("") as project:
            vxl_data = project.execute("""SELECT v.id, v.name, v.x0, v.y0,
                                                v.step, v.avg_z, v.mse_z, v.mse_plane,
                                                v.plane_id, v.scan_id, v.vxl_mdl_id
                                                FROM voxels v WHERE v.name = (?)""", (self.name,)).fetchone()
            if vxl_data is None or len(vxl_data) == 0:
                plane = Plane()
                self.plane_id = plane.plane_id
                vxl_id = project.execute("""INSERT INTO voxels (name, x0, y0, step,
                                                                avg_z, mse_z, mse_plane,
                                                                plane_id, scan_id, vxl_mdl_id) VALUES
                                                                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                                                 (self.name,
                                                                  self.lower_left_point.x,
                                                                  self.lower_left_point.y,
                                                                  self.step,
                                                                  self.avg_z,
                                                                  self.mse_z,
                                                                  self.mse_plane,
                                                                  plane.plane_id,
                                                                  self.scan.scan_id,
                                                                  self.vxl_mdl_id)).lastrowid
            else:
                vxl_id = vxl_data[0]
                self.name = vxl_data[1]
                self.lower_left_point = Point(vxl_data[2], vxl_data[3])
                self.step = vxl_data[4]
                self.avg_z = vxl_data[5]
                self.mse_z = vxl_data[6]
                self.mse_plane = vxl_data[7]
                self.plane_id = vxl_data[8]
                self.scan = Scan.get_scan_from_id(vxl_data[9])
                self.vxl_mdl_id = vxl_data[10]
            return vxl_id

    def __calk_voxel_borders(self):
        x0 = self.lower_left_point.x
        y0 = self.lower_left_point.y
        step = self.step
        return {"lower_left": Point(x0, y0),
                "upper_left": Point(x0, y0 + step),
                "upper_right": Point(x0 + step, y0 + step),
                "lower_right": Point(x0 + step, y0)
                }

    def _calk_mse_from_np_xyz_rgb(self, np_xyz_rgb, force_calk=False):
        if self.avg_z is not None and self.mse_z is not None and \
                self.mse_plane is not None and force_calk is False:
            return None

        if len(np_xyz_rgb) == 0:
            return -1
        self.avg_z = round(float(np.mean(np_xyz_rgb, axis=0)[2]), 5)
        plane = self.plane

        sum_of_z_vv = 0
        sum_of_plane_vv = 0
        for point in np_xyz_rgb:
            x, y, z = point[0], point[1], point[2]
            z_plane = plane.a * x + plane.b * y + plane.d

            sum_of_z_vv += (z - self.avg_z) ** 2
            sum_of_plane_vv += (z - z_plane) ** 2
        try:
            self.mse_z = round((sum_of_z_vv / (len(np_xyz_rgb) - 1)) ** 0.5, 5)
            self.mse_plane = round((sum_of_plane_vv / (len(np_xyz_rgb) - 1)) ** 0.5, 5)
        except ZeroDivisionError:
            self.mse_z = None
            self.mse_plane = None

        self.__update_voxel_data_in_db()
        return None

    def __insert_in_db(self):
        data = (self.name,
                self.lower_left_point.x, self.lower_left_point.y, self.step,
                self.avg_z, self.mse_z, self.mse_plane,
                self.scan.scan_id, self.vxl_mdl_id)
        with Project("") as project:
            project.execute("""INSERT INTO voxels (
            name,
            x0, y0, step,
            avg_z, mse_z, mse_plane, 
            scan_id, vxl_mdl_id) VALUES (?, 
                                         ?, ?, ?,
                                         ?, ?, ?,
                                         ?, ?)""", data)

    def __update_voxel_data_in_db(self):
        """Обновдяет данные плоскости в БД на основании атрибутов объекта"""
        with Project("") as cursor_inn:
            cursor_inn.execute("""UPDATE voxels SET
                                    name = (?),
                                    x0 = (?), y0 = (?),
                                    step = (?),
                                    avg_z = (?), mse_z = (?), mse_plane = (?), 
                                    scan_id = (?), vxl_mdl_id = (?)
                                    WHERE id = (?)
                                    ;""", (self.name,
                                           self.vxl_borders["lower_left"].x, self.vxl_borders["lower_left"].y,
                                           self.step,
                                           self.avg_z, self.mse_z, self.mse_plane,
                                           self.scan.scan_id, self.vxl_mdl_id,
                                           self.id))

    def vxl_volume(self, base_lvl=0):
        plane = self.plane
        if plane.is_calculated() is False:
            return 0
        a, b, d = plane.a, plane.b, plane.d
        points = []
        for point in self.vxl_borders.values():
            x, y = point.x, point.y
            z = a*x + b*y + d
            points.append([x, y, z])
            points.append([x, y, base_lvl])
        return ConvexHull(points).volume


if __name__ == "__main__":
    pr = Project("15")
    v1 = Voxel(Point(0, 0.05), 0.1, vxl_mdl_id=1)
    print(v1)

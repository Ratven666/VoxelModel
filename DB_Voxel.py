from DB_Point import *
from DB_ScanIterator import *
from DB_Scan import *
from DB_Plane import *


class Voxel:

    def __init__(self, lower_left_point: Point, step: float, vxl_mdl_id):
        self.lower_left_point = lower_left_point
        self.step = step
        self.vxl_mdl_id = vxl_mdl_id
        self.name = f"VXL_VM{self.vxl_mdl_id}_s{self.step}_" \
                    f"X{round(self.lower_left_point.x, 3)}_" \
                    f"Y{round(self.lower_left_point.y, 3)}"
        self.scan = Scan(Project(""), f"SC_{self.name}")
        self.plane_id = None
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
                                                v.step, v.plane_id, v.scan_id, v.vxl_mdl_id
                                                FROM voxels v WHERE v.name = (?)""", (self.name,)).fetchone()
            if vxl_data is None or len(vxl_data) == 0:
                plane = Plane()
                self.plane_id = plane.plane_id
                vxl_id = project.execute("""INSERT INTO voxels (name, x0, y0, step, 
                                                                plane_id, scan_id, vxl_mdl_id) VALUES
                                                                (?, ?, ?, ?, ?, ?, ?)""",
                                                                 (self.name,
                                                                  self.lower_left_point.x,
                                                                  self.lower_left_point.y,
                                                                  self.step,
                                                                  plane.plane_id,
                                                                  self.scan.scan_id,
                                                                  self.vxl_mdl_id)).lastrowid
            else:
                vxl_id = vxl_data[0]
                self.name = vxl_data[1]
                self.lower_left_point = Point(vxl_data[2], vxl_data[3])
                self.step = vxl_data[4]
                self.plane_id = vxl_data[5]
                self.scan = Scan.get_scan_from_id(vxl_data[6])
                self.vxl_mdl_id = vxl_data[7]
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

    def __insert_in_db(self):
        data = (self.name,
                self.lower_left_point.x, self.lower_left_point.y, self.step,
                self.scan.scan_id, self.vxl_mdl_id)
        with Project("") as project:
            project.execute("""INSERT INTO voxels (
            name,
            x0, y0, step, 
            scan_id, vxl_mdl_id) VALUES (?, 
                                         ?, ?, ?,
                                         ?, ?)""", data)


if __name__ == "__main__":
    pr = Project("15")
    v1 = Voxel(Point(0, 0.01), 0.1, vxl_mdl_id=1)
    print(v1)

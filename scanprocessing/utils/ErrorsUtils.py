from scanprocessing.classes.Voxel import *


class ErrorsUtils:

    def __init__(self, obj):
        self.errors = {}
        if type(obj) is Voxel:
            self.calc_z_mse(obj)
            self.calc_distance_mse(obj)

    @staticmethod
    def __calc_mse_from_seq(deviations):
        sum_of_vv = 0
        n = 0
        for deviation in deviations:
            sum_of_vv += deviation ** 2
            n += 1
        if n == 0:
            return None
        return (sum_of_vv / float(n-1)) ** 0.5

    @staticmethod
    def __calk_delta_z_between_point_and_plane(voxel: Voxel):
        if voxel.plane is None:
            return None
        a, b, d = voxel.plane.a, voxel.plane.b, voxel.plane.d
        for point in voxel.scan.points:
            yield (a * point.x + b * point.y + d) - point.z

    @staticmethod
    def __calk_distance_between_point_and_plane(voxel: Voxel):
        if voxel.plane is None:
            return None
        a, b = voxel.plane.a, voxel.plane.b
        c, d = voxel.plane.c, voxel.plane.d
        for point in voxel.scan.points:
            distance = abs((a * point.x)+(b * point.y)+(c * point.z)+d) / (((a ** 2)+(b ** 2)+(c ** 2))**0.5)
            yield distance

    def calc_z_mse(self, voxel: Voxel):
        gen = ErrorsUtils.__calk_delta_z_between_point_and_plane(voxel)
        z_mse = ErrorsUtils.__calc_mse_from_seq(gen)
        self.errors["z_mse"] = z_mse

    def calc_distance_mse(self, voxel: Voxel):
        gen = ErrorsUtils.__calk_distance_between_point_and_plane(voxel)
        dist_mse = ErrorsUtils.__calc_mse_from_seq(gen)
        self.errors["dist_mse"] = dist_mse

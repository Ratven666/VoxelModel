class ScanUtils:

    @staticmethod
    def parse_xyz_points_from_file(path_to_file: str):
        with open(path_to_file, "r") as file:
            for line in file:
                print(line)

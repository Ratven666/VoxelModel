# import numpy as np
import scipy
from scipy.spatial import ConvexHull

# points = np.array([[0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0], [1, 1, 1], [1, 0, 1], [0, 0, 0]])  # your points
volume = scipy.spatial.ConvexHull([[0, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 0]]).volume
#
# points = np.array([[0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0], [1, 1, 1], [1, 0, 1], [0, 0, 0]])  # your points
# volume = scipy.spatial.ConvexHull(points).volume

print(volume)

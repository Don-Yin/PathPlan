import numpy as np
import numba


def point_to_numpy_idx(coord: tuple, itk_image, round: bool = True):
    """
    Convert a point in the physical space to a numpy index
    :param coord: the point in the physical space
    :param itk_image: the image to which the point belongs
    :return: the numpy index
    """
    # (point - offset) * inverse of the (direction matrix * spacing matrix) = index
    offset = itk_image.GetOrigin()
    direction = itk_image.GetDirection()
    spacing = itk_image.GetSpacing()

    idx = np.subtract(coord, offset)  # (point - offset)

    direction = np.reshape(direction, (3, 3))  # reshape
    spacing = np.reshape(spacing, (1, 3))  # reshape

    product = [
        direction[0] * spacing[0][0],
        direction[1] * spacing[0][1],
        direction[2] * spacing[0][2],
    ]  # a bit strange but works
    product = np.array(product)  # convert to numpy array

    product = np.linalg.inv(product)  # inverse
    idx = np.matmul(product, idx)  # multiply
    idx = np.round(idx).astype(int) if round else idx  # round and convert to int

    return idx


def points_to_linear(point_1, point_2):
    """
    Calculate the linear equation of the line that passes through two points
    :param point_1: the first point (x, y, z)
    :param point_2: the second point (x, y, z)
    :return: the linear equation as a function of x, y, z
    """
    x1, y1, z1 = point_1
    x2, y2, z2 = point_2
    vector = np.array([x2 - x1, y2 - y1, z2 - z1])
    point_on_line = np.array([x1, y1, z1])

    def linear_equation_3d(coordinates):
        point = np.array(coordinates)
        vector_to_point = point - point_on_line
        projection = np.dot(vector_to_point, vector) / np.dot(vector, vector)
        closest_point_on_line = point_on_line + projection * vector
        distance = np.linalg.norm(point - closest_point_on_line)
        return distance

    return linear_equation_3d


def get_idx_between_points(arr, point_1, point_2):
    """
    Get the indices of the array that the line passes through
    :param arr: the array
    :param point_1: the first point (x, y, z)
    :param point_2: the second point (x, y, z)
    :return: the indices of the array that the line passes through
    """
    linear_equation = points_to_linear(point_1, point_2)
    indices = []
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            for k in range(arr.shape[2]):
                if np.isclose(linear_equation((i, j, k)), 0, rtol=1e-5, atol=0.5):  # relative and absolute tolerance
                    indices.append((i, j, k))
    return indices


if __name__ == "__main__":
    # func, value = points_to_linear((0, 0, 0), (1, 1, 1))
    pass

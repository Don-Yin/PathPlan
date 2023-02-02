import pandas


def reverse_negative_idx(shape, indices):
    """
    Reverse negative indices to positive indices.
    :param shape: shape of the image
    :param target: target indices
    :return: target indices with positive indices
    """
    for i in range(len(indices)):
        for j in range(len(indices[i])):
            if indices[i][j] < 0:
                indices[i][j] += shape[j]
    return indices


def points_to_line(point_1, point_2):
    line = {
        "x": [point_1[0], point_2[0] + 2 * (point_2[0] - point_1[0])],  # extend the line
        "y": [point_1[1], point_2[1] + 2 * (point_2[1] - point_1[1])],
        "z": [point_1[2], point_2[2] + 2 * (point_2[2] - point_1[2])],
    }
    line = pandas.DataFrame(line)
    return line

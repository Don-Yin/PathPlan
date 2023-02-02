import unittest
from src.utils.linear import points_to_linear, get_idx_between_points
import numpy as np
from src.utils.general import reverse_negative_idx


class Test(unittest.TestCase):
    def test_points_to_linear(self):
        """
        Test the points_to_linear function
        the function should return a linear equation and the expected value
        """
        point_1 = (0, 0, 0)
        point_2 = (1, 1, 1)
        linear = points_to_linear(point_1, point_2)
        self.assertEqual(linear((0, 0, 0)), 0)
        self.assertEqual(linear((1, 1, 1)), 0)
        self.assertEqual(linear((0.5, 0.5, 0.5)), 0)

    def test_get_idx_from_line(self):
        """
        Test the get_idx_from_line function
        the function should return the indices of the line between two points
        """
        # 3d array
        arr = np.zeros((3, 4, 4))
        indices = get_idx_between_points(arr, (0, 0, 0), (3, 4, 4))
        # the diagonal line should pass through all the indices
        diagonal_1 = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
        diagonal_2 = [(0, 2, 2), (1, 1, 1), (2, 0, 0)]

        self.assertTrue(set(diagonal_1).issubset(set(indices)))
        self.assertFalse(set(diagonal_2).issubset(set(indices)))

    def test_reverse_negative_idx(self):
        """
        Test the reverse_negative_idx function
        the function should return the indices of positive values instead of negative values
        """
        arr = np.zeros((3, 3, 3))
        indices = [[-1, -1, -1]]
        self.assertEqual(reverse_negative_idx(arr.shape, indices), [[2, 2, 2]])


if __name__ == "__main__":
    unittest.main()

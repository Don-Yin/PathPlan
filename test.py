"""
This file contains unit tests for the mesh functions for intersection checking and marching cubes
"""

import unittest
import numpy as np
from src.utils.marching_cubes import check_angle_of_intersection, check_distance_intersection
import numpy as np


class Test(unittest.TestCase):
    def test_intersection(self):
        """
        Test that the angle of intersection is 0 when the line intersects the surface
        """
        p1 = np.array([0, 0, 0], dtype=np.float64)
        p2 = np.array([1, 1, 1], dtype=np.float64)
        verts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)
        faces = np.array([[0, 1, 2]])
        expected_angle = 0
        self.assertAlmostEqual(check_angle_of_intersection(p1, p2, verts, faces), expected_angle, delta=1e-10)

    def test_no_intersection(self):
        """
        Test that the angle of intersection is False when the line does not intersect the surface
        """
        p1 = np.array([0, 0, 0], dtype=np.float64)
        p2 = np.array([1, 0, 0], dtype=np.float64)
        verts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)
        faces = np.array([[0, 1, 2]])
        expected_result = False
        self.assertEqual(check_angle_of_intersection(p1, p2, verts, faces), expected_result)

    def test_distance_intersection(self):
        """
        Test that the distance of intersection is 0 when the line intersects the surface
        """
        p1 = np.array([0, 0, 0], dtype=np.float64)
        p2 = np.array([1, 1, 1], dtype=np.float64)
        verts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)
        faces = np.array([[0, 1, 2]])
        expected_distance = 0
        self.assertAlmostEqual(check_distance_intersection(p1, p2, verts, faces), expected_distance, delta=1e-10)


if __name__ == "__main__":
    unittest.main()

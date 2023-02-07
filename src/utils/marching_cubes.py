import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from skimage import measure
from numba import njit


def marching_cubes(volume: np.ndarray, level: float = 0.5, visualize=False, lines: list = None):
    """Generates a 3D mesh using the Marching Cubes algorithm.

    This function uses the `marching_cubes` function from the `measure` module
    to extract the surface mesh of a 3D volume. Optionally, it can also display
    a 3D visualization of the mesh using matplotlib.

    Args:
        volume (np.ndarray): A 3D numpy array representing the input volume.
        level (float, optional): The isosurface level to be extracted from the volume.
            Defaults to 0.5.
        visualize (bool, optional): If `True`, a 3D visualization of the mesh is shown.
            Defaults to `False`.
        lines (list, optional): A list of lines to be plotted in the 3D visualization.
            Each line is represented as a tuple of two 3D points. Defaults to `None`.

    Returns:
        tuple: A tuple containing the vertices, faces, normals, and values of the mesh.
    """
    # Use marching cubes to obtain the surface mesh of these ellipsoids
    verts, faces, normals, values = measure.marching_cubes(volume, level=level)

    if visualize:
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection="3d")

        # Fancy indexing: `verts[faces]` to generate a collection of triangles
        mesh = Poly3DCollection(verts[faces])
        mesh.set_edgecolor("k")
        ax.add_collection3d(mesh)

        if lines is not None:
            for line in lines:
                ax.plot(
                    [line[0][0], line[1][0]],
                    [line[0][1], line[1][1]],
                    [line[0][2], line[1][2]],
                    "r-",
                )

        ax.set_xlabel("x-axis:")
        ax.set_ylabel("y-axis:")
        ax.set_zlabel("z-axis:")

        # set the limits of the plot to the limits of the data
        ax.set_xlim(0, volume.shape[0])
        ax.set_ylim(0, volume.shape[1])
        ax.set_zlim(0, volume.shape[2])

        plt.tight_layout()
        plt.show()

    return verts, faces, normals, values


@njit()
def ray_triangle_intersection(p, d, verts, face):
    """
    Check if a ray intersects with a triangle.

    Parameters
    ----------
    p : np.ndarray
        The origin of the ray.
    d : np.ndarray
        The direction of the ray.
    verts : np.ndarray
        An array of vertices.
    face : np.ndarray
        A triangle defined by three vertex indices.

    Returns
    -------
    bool
        True if the ray intersects with the triangle.
    """
    e1 = verts[face[1]] - verts[face[0]].astype(np.float64)
    e2 = verts[face[2]] - verts[face[0]].astype(np.float64)

    h = np.cross(d, e2).astype(np.float64)
    a = np.dot(e1, h)

    if a > -1e-10 and a < 1e-10:
        return False
    f = 1.0 / a
    s = p - verts[face[0]]
    u = f * np.dot(s, h)
    if u < 0.0 or u > 1.0:
        return False
    q = np.cross(s, e1)
    v = f * np.dot(d, q)
    if v < 0.0 or u + v > 1.0:
        return False
    t = f * np.dot(e2, q)
    # if t > 1e-10: # ray intersection
    if t > 1e-10 and t < 1:  # between the two points
        return True
    else:
        return False


@njit()
def check_angle_of_intersection(p1, p2, verts, faces):
    """
    Calculates the minimum angle between the ray and the normal vector of the triangle surface.

    Args:
    ----
    p1: np.ndarray
        start point of the ray
    p2: np.ndarray
        end point of the ray
    verts: np.ndarray
        an array of vertices of the triangle surface
    faces: np.ndarray
        an array of faces of the triangle surface

    Returns:
    -------
    float or bool:
        Returns the minimum angle between the ray and the normal vector of the triangle surface if the ray intersects with the triangle surface, False
    """

    d = p2 - p1

    for face in faces:
        e1 = verts[face[1]] - verts[face[0]].astype(np.float64)
        e2 = verts[face[2]] - verts[face[0]].astype(np.float64)

        h = np.cross(d, e2).astype(np.float64)
        a = np.dot(e1, h)

        if a > -1e-10 and a < 1e-10:
            continue
        f = 1.0 / a
        s = p1 - verts[face[0]]
        u = f * np.dot(s, h)
        if u < 0.0 or u > 1.0:
            continue
        q = np.cross(s, e1)
        v = f * np.dot(d, q)
        if v < 0.0 or u + v > 1.0:
            continue
        t = f * np.dot(e2, q)
        # if t > 1e-10: # ray intersection
        if t > 1e-10 and t < 1:  # between the two points
            # Calculate the normal vector of the surface
            normal = np.cross(e1, e2)
            normal /= np.linalg.norm(normal)
            # Calculate the angle between the ray and the normal vector
            angle = np.arccos(np.dot(d, normal) / (np.linalg.norm(d) * np.linalg.norm(normal)))
            # Get the minimum of the angle and its complementary angle (90 - angle)
            if angle > np.pi / 2:
                angle = np.pi - angle
            angle = np.rad2deg(angle)
            return angle
    return False


@njit()
def check_intersect(p1, p2, verts, faces):
    """
    Check if a line intersects with a triangle surface.
    A wrapper function for ray_triangle_intersection.

    Args:
    ----
    p1: np.ndarray
        start point of the line

    p2: np.ndarray
        end point of the line

    verts: np.ndarray
        an array of vertices of the triangle surface

    faces: np.ndarray
        an array of faces of the triangle surface

    Returns:
        bool:
            True if the line intersects with the triangle surface, False otherwise
    """
    # Cast a ray from one point to the other
    d = p2 - p1
    # Check if the ray intersects with any of the triangular faces
    for face in faces:
        if ray_triangle_intersection(p1, d, verts, face):  # print("The line intersects with the marching cubes surface.")
            return True
    else:  # print("The line does not intersect with the marching cubes surface.")
        return False


if __name__ == "__main__":
    import os
    from pathlib import Path
    import SimpleITK as sitk
    import numpy as np

    from timeit import timeit

    test_images = os.listdir(Path("week-2", "practicals", "TestSet"))
    test_images_itk: dict = {i: sitk.ReadImage(Path("week-2", "practicals", "TestSet") / i) for i in test_images}

    # # convert entries and targets to numpy indices
    array_hippo = sitk.GetArrayFromImage(test_images_itk["r_hippoTest.nii.gz"])
    array_hippo = np.rot90(array_hippo, 1, axes=(0, 2))

    # combine ventriclesTest and vesselsTestDilate1 into one array
    array_ventricles = sitk.GetArrayFromImage(test_images_itk["ventriclesTest.nii.gz"])
    array_vessels = sitk.GetArrayFromImage(test_images_itk["vesselsTestDilate1.nii.gz"])
    array_ventricles_vessels = np.logical_or(array_ventricles, array_vessels)

    array_ventricles = np.rot90(array_ventricles, 1, axes=(0, 2))
    array_vessels = np.rot90(array_vessels, 1, axes=(0, 2))
    array_ventricles_vessels = np.rot90(array_ventricles_vessels, 1, axes=(0, 2))

    # r_cortexTest.nii.gz
    array_cortex = sitk.GetArrayFromImage(test_images_itk["r_cortexTest.nii.gz"])
    array_cortex = np.rot90(array_cortex, 1, axes=(0, 2))

    # marching cubes
    verts_hippo, faces_hippo, _, _ = marching_cubes(array_hippo, 0.5)
    verts_ventricles, faces_ventricles, _, _ = marching_cubes(array_ventricles, 0.5)
    verts_vessels, faces_vessels, _, _ = marching_cubes(array_vessels, 0.5)
    verts_ventricles_vessels, faces_ventricles_vessels, _, _ = marching_cubes(array_ventricles_vessels, 0.5)
    verts_cortex, faces_cortex, _, _ = marching_cubes(array_cortex, 0.5)

    # dummy points
    p1 = np.array([0, 0, 0])
    p2 = np.array([3, 2, 1])

    # time the function
    print(timeit(lambda: check_intersect(p1, p2, verts_hippo, faces_hippo), number=1000))  # 5.8907715419999995
    print(timeit(lambda: check_intersect(p1, p2, verts_ventricles, faces_ventricles), number=1000))  # 21.919658

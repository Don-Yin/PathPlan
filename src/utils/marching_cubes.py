import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from skimage import measure
from skimage.draw import ellipsoid


def marching_cubes(volume: np.ndarray, level: float = 0.5):
    """
    Show volume with matplotlib
    :param volume: 3D numpy array
    :param level: level of the surface
    :return: None
    """
    # Use marching cubes to obtain the surface mesh of these ellipsoids
    verts, faces, normals, values = measure.marching_cubes(volume, level=level)

    # Display resulting triangular mesh using Matplotlib. This can also be done
    # with mayavi (see skimage.measure.marching_cubes_lewiner docstring).
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection="3d")

    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    mesh = Poly3DCollection(verts[faces])
    mesh.set_edgecolor("k")
    ax.add_collection3d(mesh)

    ax.set_xlabel("x-axis:")
    ax.set_ylabel("y-axis:")
    ax.set_zlabel("z-axis:")

    # ax.set_xlim(0, 24)  # a = 6 (times two for 2nd ellipsoid)
    # ax.set_ylim(0, 20)  # b = 10
    # ax.set_zlim(0, 32)  # c = 16

    # set the limits of the plot to the limits of the data
    ax.set_xlim(0, volume.shape[0])
    ax.set_ylim(0, volume.shape[1])
    ax.set_zlim(0, volume.shape[2])

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    dummy = np.random.rand(10, 10, 10)
    marching_cubes(volume=dummy, level=0.5)

# Import data
import time
import numpy as np
import plotly.graph_objects as go
from skimage import io
from plotly import offline
import pandas
import plotly.express as px
import SimpleITK as sitk


def frame_args(duration):
    return {
        "frame": {"duration": duration},
        "mode": "immediate",
        "fromcurrent": True,
        "transition": {"duration": duration, "easing": "linear"},
    }


def show_volume(
    volume: sitk,
    entries: np.ndarray = None,
    targets: np.ndarray = None,
    valid_entries_targets: list[tuple] = None,
    meshes: list[tuple[np.ndarray, np.ndarray]] = None,
):
    """
    Show volume with plotly
    :param volume: 3D numpy array
    :param entries: 2D numpy array containing the coordinates of the entries
    :param targets: 2D numpy array containing the coordinates of the targets
    :param valid_entries_targets: list of tuples containing the indices of the valid entries and targets; used for drawing lines
    :return: None
    """
    # correct orientation
    volume = sitk.GetArrayFromImage(volume)

    # some preprocess to align the image
    volume = volume.T
    volume = np.flip(volume, axis=1)
    volume = np.rot90(volume, 3, axes=(0, 2))

    r, c = volume[0].shape

    # Define frames
    nb_frames = volume.shape[0]
    offset = volume.shape[0] - 1
    cmax = np.max(volume)
    cmin = np.min(volume)

    fig = go.Figure(
        frames=[
            go.Frame(
                data=go.Surface(
                    z=(nb_frames - k) * np.ones((r, c)),
                    surfacecolor=np.flipud(volume[offset - k]),
                    cmin=cmin,
                    cmax=cmax,
                ),
                name=str(k),  # you need to name the frame for the animation to behave properly
            )
            for k in range(nb_frames)
        ]
    )

    # Add data to be displayed before animation starts
    fig.add_trace(
        go.Surface(
            z=nb_frames * np.ones((r, c)),
            surfacecolor=np.flipud(volume[offset]),
            colorscale="Gray",
            cmin=cmin,
            cmax=cmax,
            colorbar=dict(thickness=20, ticklen=4),
        )
    )

    # Add entries and targets --------------------------------------------

    fig.add_trace(
        go.Scatter3d(
            x=entries[:, 0],
            y=entries[:, 1],
            z=entries[:, 2],
            mode="markers",
            marker=dict(size=3, color="red"),
        )
    )
    fig.add_trace(
        go.Scatter3d(
            x=targets[:, 0],
            y=targets[:, 1],
            z=targets[:, 2],
            mode="markers",
            marker=dict(size=3, color="green"),
        )
    )

    # add line --------------------------------------------
    for pair in valid_entries_targets:
        entry = pair[0]  # an array of 3 elements
        target = pair[1]  # an array of 3 elements
        line = {
            "x": [entry[0], target[0]],
            "y": [entry[1], target[1]],
            "z": [entry[2], target[2]],
        }
        line = pandas.DataFrame(line)
        fig.add_trace(
            go.Scatter3d(
                x=line.x,
                y=line.y,
                z=line.z,
                mode="lines",
                line=dict(color="green", width=3),
            )
        )

    # add verts and faces --------------------------------------------

    # get a color plate for the mesh
    colors = px.colors.qualitative.Plotly

    for mesh in meshes:
        fig.add_trace(
            go.Mesh3d(
                x=mesh["verts"][:, 0],
                y=mesh["verts"][:, 1],
                z=mesh["verts"][:, 2],
                i=mesh["faces"][:, 0],
                j=mesh["faces"][:, 1],
                k=mesh["faces"][:, 2],
                color=colors[meshes.index(mesh)],
                opacity=0.5,
            )
        )

    sliders = [
        {
            "pad": {"b": 10, "t": 60},
            "len": 0.9,
            "x": 0.4,
            "y": 0,
            "steps": [
                {
                    "args": [[f.name], frame_args(0)],
                    "label": str(k),
                    "method": "animate",
                }
                for k, f in enumerate(fig.frames)
            ],
        }
    ]

    # Layout
    fig.update_layout(
        title="Slices in volumetric data",
        width=1200,  # of the view window
        height=750,  # of the view window
        scene=dict(
            zaxis=dict(range=[-0.1, nb_frames], autorange=False),
            aspectratio=dict(x=1, y=1, z=1),
        ),
        updatemenus=[
            {
                "direction": "left",
                "pad": {"r": 10, "t": 70},
                "type": "buttons",
                "x": 0.1,
                "y": 0,
            }
        ],
        sliders=sliders,
    )

    offline.plot(fig)  # instead of fig.show()


if __name__ == "__main__":
    vol = io.imread("https://s3.amazonaws.com/assets.datacamp.com/blog_assets/attention-mri.tif")
    volume = vol.T
    show_volume(volume)

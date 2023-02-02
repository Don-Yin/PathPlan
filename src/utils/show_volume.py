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


def show_volume(volume: sitk, entries: np.ndarray = None, targets: np.ndarray = None, lines: list[pandas.DataFrame] = None):

    """
    Show volume with plotly
    :param volume: 3D numpy array
    :param entries: 2D numpy array containing the coordinates of the entries
    :param targets: 2D numpy array containing the coordinates of the targets
    :return: None
    """
    # volumes = [sitk.GetArrayFromImage(i) for i in images_itk]
    # assert len(set([i.shape for i in volumes])) == 1, "Volumes are not the same size"

    volume = sitk.GetArrayFromImage(volume)
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

    # end of entries and targets -----------------------------------------

    # add line --------------------------------------------
    for line in lines:
        fig.add_trace(
            go.Scatter3d(
                # extend the line to the end of the volume
                x=line["x"],
                y=line["y"],
                z=line["z"],
                mode="lines",
                line=dict(color="green", width=2),
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
                "buttons": [
                    {
                        "args": [None, frame_args(50)],
                        "label": "&#9654;",  # play symbol
                        "method": "animate",
                    },
                    {
                        "args": [[None], frame_args(0)],
                        "label": "&#9724;",  # pause symbol
                        "method": "animate",
                    },
                ],
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

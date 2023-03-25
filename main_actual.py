"""
This file is the main file for the actual set. It checks the validity of the entries and targets and saves the valid ones.
This is identical to the main_testset.py file, except some variable names.
"""

import SimpleITK as sitk
from pathlib import Path
import os
from src.utils.show_volume import show_volume
from src.utils.marching_cubes import marching_cubes, check_intersect, check_angle_of_intersection
import numpy as np
from src.modules.fcsv import FCSV
from src.utils.linear import point_to_numpy_idx
from itertools import product
from tqdm import tqdm
from random import shuffle
import multiprocessing as mp

# read the entries and targets
entires = FCSV(Path("week-2", "practicals", "entries.fcsv"))
targets = FCSV(Path("week-2", "practicals", "targets.fcsv"))

entries_coords = entires.content_df[["x", "y", "z"]].to_numpy()
targets_coords = targets.content_df[["x", "y", "z"]].to_numpy()

# read the images
images_names = os.listdir(Path("week-2", "practicals", "BrainParcellation"))
images_itk: dict = {i: sitk.ReadImage(Path("week-2", "practicals", "BrainParcellation") / i) for i in images_names}

# prepare the data as numpy arrays
images_array: dict = {i: sitk.GetArrayFromImage(images_itk[i]) for i in images_names}
images_array: dict = {i: np.rot90(images_array[i], 1, axes=(0, 2)) for i in images_names}
# combine the ventricles and vessels into one so that we can check for intersection with them
images_array["ventricles_vessels"] = np.logical_or(
    images_array["ventricles.nii.gz"],
    images_array["vessels.nii.gz"],
)

# prepare the meshes iteratively
images_meshes = {}
for i in images_array.keys():
    verts, faces, _, _ = marching_cubes(images_array[i], 0.5)
    images_meshes[i] = {}
    images_meshes[i]["verts"] = verts
    images_meshes[i]["faces"] = faces

# convert real-world coordinates to numpy indices
entries_coords_idx_unrounded = [point_to_numpy_idx(i, list(images_itk.values())[0]) for i in entries_coords]
entries_coords_idx_unrounded_array = np.array(entries_coords_idx_unrounded)
targets_coords_idx_unrounded = [point_to_numpy_idx(i, list(images_itk.values())[0]) for i in targets_coords]
targets_coords_idx_unrounded_array = np.array(targets_coords_idx_unrounded)

# make a column of entries and targets np index for the entries and targets in content_df
entires.content_df["idx"] = [tuple(i) for i in entries_coords_idx_unrounded]
targets.content_df["idx"] = [tuple(i) for i in targets_coords_idx_unrounded]

entries_dict = {i: j for i, j in zip(entires.content_df["idx"], entires.content_df["id"])}
targets_dict = {i: j for i, j in zip(targets.content_df["idx"], targets.content_df["id"])}

entries_targets_combs = list(product(entries_coords_idx_unrounded_array, targets_coords_idx_unrounded_array))
# entries_targets_combs = entries_targets_combs[:5000]


def check_validity(entry_target_tuple):
    """
    Check the validity of an entry and target tuple.

    The function checks if the entry and target intersect with the right hippocampus, ventricles and vessels, and cortex. If the entry and target intersect with the right hippocampus and the angle of intersection with the cortex is greater than (90 - 55) degrees, the function returns False. Otherwise, the function returns True.

    Parameters:
    - entry_target_tuple (tuple): A tuple of entry and target.

    Returns:
    - bool: The validity of the entry and target tuple.
    """

    entry, target = entry_target_tuple

    if not check_intersect(
        entry, target, verts=images_meshes["r_hippo.nii.gz"]["verts"], faces=images_meshes["r_hippo.nii.gz"]["faces"]
    ):
        return False

    if check_intersect(
        entry, target, verts=images_meshes["ventricles_vessels"]["verts"], faces=images_meshes["ventricles_vessels"]["faces"]
    ):
        return False

    if check_angle_of_intersection(  # since i am taking the normal we want it to be smaller
        entry, target, verts=images_meshes["cortex.nii.gz"]["verts"], faces=images_meshes["cortex.nii.gz"]["faces"]
    ) > (90 - 55):
        return False

    return True


def main():
    # print image dimensions
    print("Image dimensions:")
    [print(i.GetSize()) for i in images_itk.values()]
    print(f"Number of points in entries: {entires.content_df.shape[0]}")
    print(f"Number of points in targets: {targets.content_df.shape[0]}")

    # one progress bar for all the combinations
    with mp.Pool(mp.cpu_count()) as pool:
        entries_targets_combs_bool = list(
            tqdm(pool.imap(check_validity, entries_targets_combs), total=len(entries_targets_combs))
        )

    # map to entries_targets_combs using the bool list as a mask using multiple processes
    entries_targets_combs_valid = [i for i, j in zip(entries_targets_combs, entries_targets_combs_bool) if j]

    # comment out the meshes you don't want to show
    meshes = [
        images_meshes["r_hippo.nii.gz"],
        # images_meshes["ventricles.nii.gz"],
        # images_meshes["vessels.nii.gz"],
        # images_meshes["cortex.nii.gz"],
    ]

    show_volume(
        images_itk["r_hippo.nii.gz"],
        entries_coords_idx_unrounded_array,  # for point plotting
        targets_coords_idx_unrounded_array,
        valid_entries_targets=entries_targets_combs_valid[:100],  # for line plotting; visualize only the first 100 to save time
        meshes=meshes,
    )

    # convert the valid entries_targets_combs to a id using the entries and targets content_df
    entries_targets_combs_valid_ids = [(entries_dict[tuple(i)], targets_dict[tuple(j)]) for i, j in entries_targets_combs_valid]

    return entries_targets_combs_valid_ids


if __name__ == "__main__":
    selected_entries_targets = main()
    print(f"Number of valid entries and targets: {len(selected_entries_targets)}")

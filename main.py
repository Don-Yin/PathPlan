import SimpleITK as sitk
from pathlib import Path
import os
from src.utils.show_volume import show_volume
from src.utils.marching_cubes import marching_cubes
import numpy as np
from src.modules.fcsv import FCSV
from src.utils.linear import point_to_numpy_idx, points_to_linear, get_idx_between_points
import pandas
from src.utils.general import reverse_negative_idx, points_to_line
from itertools import product
from tqdm import tqdm


if __name__ == "__main__":
    # Task 0.
    # a.	Load all the files located in the TestSet.
    test_images = os.listdir(Path("week-2", "practicals", "TestSet"))
    test_images_itk = {i: sitk.ReadImage(Path("week-2", "practicals", "TestSet") / i) for i in test_images}
    print(test_images_itk.keys())
    # i. What are the dimensions of the image
    [print(i.GetSize()) for i in test_images_itk.values()]

    # print(test_images_itk[0].GetDirection() * test_images_itk[0].GetSpacing())

    # ii. What are the number of points in the entries and targets fiducials
    entires = FCSV(Path("week-2", "practicals", "entries.fcsv"))
    targets = FCSV(Path("week-2", "practicals", "targets.fcsv"))
    num_points_entries = entires.content_df.shape[0]
    num_points_targets = targets.content_df.shape[0]

    print(f"Number of points in entries: {num_points_entries}")
    print(f"Number of points in targets: {num_points_targets}")

    # make marching cubes
    # marching_cubes(sitk.GetArrayFromImage(test_images_itk[1]), level=0.5)

    # # d. Repeat these tasks for the files in BrainParcellation. Note how the sizes differ.

    # brain_images = Path("week-2", "practicals", "BrainParcellation").glob("*.nii.gz")
    # brain_images_itk = [sitk.ReadImage(i) for i in brain_images]

    # entries_coords_idx = np.array([point_to_numpy_idx(i, brain_images_itk[4]) for i in entries_coords])
    # targets_coords_idx = np.array([point_to_numpy_idx(i, brain_images_itk[4]) for i in targets_coords])
    # show_volume(sitk.GetArrayFromImage(brain_images_itk[4]), entries_coords_idx, targets_coords_idx)

    # Task 1. Given the following statements, write a corresponding formal mathematical test
    # a. Placement of an electrode for recording temporal lobe epilepsy must target the hippocampus (r_hippo.nii.gz)
    # b. Placement must avoid penetrating the ventricles (ventricles.nii.gz) to prevent cerebrospinal fluid leakage.
    # c. Placement must avoid hitting any blood vessels (vessels.nii.gz) to prevent haemorrhage.
    # d. Electrodes may deflect if not perpendicular (<55°) to cortex (cortex.nii.gz) upon entry. I.E. tool placement should be placed similar to green trajectory, the orange trajectory is too shear:

    # ----------------- Task 1 -----------------
    # convert entries and targets to numpy indices
    entries_coords = entires.content_df[["x", "y", "z"]].to_numpy()
    targets_coords = targets.content_df[["x", "y", "z"]].to_numpy()

    # a. Placement of an electrode for recording temporal lobe epilepsy must target the hippocampus (r_hippo.nii.gz)
    shape = test_images_itk["r_hippoTest.nii.gz"].GetSize()

    # convert real-world coordinates to numpy indices
    entries_coords_idx_unrounded = np.array(
        [point_to_numpy_idx(i, test_images_itk["r_hippoTest.nii.gz"], round=False) for i in entries_coords]
    )
    targets_coords_idx_unrounded = np.array(
        [point_to_numpy_idx(i, test_images_itk["r_hippoTest.nii.gz"], round=False) for i in targets_coords]
    )
    entries_coords_idx_unrounded = reverse_negative_idx(shape, entries_coords_idx_unrounded)
    targets_coords_idx_unrounded = reverse_negative_idx(shape, targets_coords_idx_unrounded)

    data = sitk.GetArrayFromImage(test_images_itk["r_hippoTest.nii.gz"])
    print(set(data.flatten()))  # {0, 1} -> binary

    entries_targets_combs = list(product(entries_coords_idx_unrounded, targets_coords_idx_unrounded))

    # visual check
    lines = [points_to_line(i[0], i[1]) for i in zip(entries_coords_idx_unrounded, targets_coords_idx_unrounded)]
    lines = lines[:3]  # take 3 lines for visualization
    # testing the visualization
    show_volume(test_images_itk["r_hippoTest.nii.gz"], entries_coords_idx_unrounded, targets_coords_idx_unrounded, lines)

    indices = [get_idx_between_points(data, i[0], i[1]) for i in tqdm(entries_targets_combs)]
    # if any of the indices on the data are 1, then the line is in the hippocampus, keep
    indices_keep = [(i, indices.index(i)) for i in indices if any(data[i] == 1)]

    print(f"Number of lines in hippocampus: {len(indices_keep)}")

    # line = points_to_line(test_entry, test_target)
    # lines = [points_to_line(i[0], i[1]) for i in tqdm(entry_target_combs)][:5]

    # insert other criteria here later (ventricles, vessels, cortex); time permitting

    final_lines = [entries_targets_combs[i[1]] for i in indices_keep]
    show_volume(test_images_itk["r_hippoTest.nii.gz"], entries_coords_idx_unrounded, targets_coords_idx_unrounded, final_lines)

    # to be continued...

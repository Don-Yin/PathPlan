"""
This script is used to check the source of exclusion for the test set.
I.e., if the entry-target pair is excluded because it is in the ventricles or vessels, or because it is too shear the cortex.
"""

import json
from matplotlib import pyplot as plt
from supervenn import supervenn
from src.utils.marching_cubes import check_intersect, check_angle_of_intersection
from main_testset import images_meshes, entries_targets_combs
import multiprocessing as mp
from tqdm import tqdm
import os


def check_source_validity(entry_target_tuple):
    entry, target = entry_target_tuple
    conditions = []
    if not check_intersect(
        entry, target, verts=images_meshes["r_hippoTest.nii.gz"]["verts"], faces=images_meshes["r_hippoTest.nii.gz"]["faces"]
    ):
        conditions.append("not intersect with hippo campus")
    if check_angle_of_intersection(
        entry, target, verts=images_meshes["r_cortexTest.nii.gz"]["verts"], faces=images_meshes["r_cortexTest.nii.gz"]["faces"]
    ) > (90 - 55):
        conditions.append("too shear cortex")
    if check_intersect(
        entry, target, verts=images_meshes["ventricles_vessels"]["verts"], faces=images_meshes["ventricles_vessels"]["faces"]
    ):
        conditions.append("in vessels or ventricles")
    return conditions


# check source of exclusion for the first time (takes a while)
if not os.path.exists("sources.json"):
    with mp.Pool(mp.cpu_count()) as pool:
        sources = list(tqdm(pool.imap(check_source_validity, entries_targets_combs), total=len(entries_targets_combs)))

    with open("sources.json", "w") as writer:
        json.dump(sources, writer)
else:
    with open("sources.json", "r") as reader:
        sources = json.load(reader)

# visualize the sources of exclusion using circles
sources = [set(i) for i in sources]
not_intersect_with_hippo_campus = set([index for index, i in enumerate(sources) if "not intersect with hippo campus" in i])
too_shear_cortex = set([index for index, i in enumerate(sources) if "too shear cortex" in i])
in_vessels_or_ventricles = set([index for index, i in enumerate(sources) if "in vessels or ventricles" in i])

supervenn(
    [
        not_intersect_with_hippo_campus,
        too_shear_cortex,
        in_vessels_or_ventricles,
    ],
    ["not intersect with hippo campus", "too shear cortex", "in vessels or ventricles"],
    side_plots=False,
)

plt.show()

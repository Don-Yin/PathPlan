# SRI - Practicals
This repository contains the practicals for SRI course

## Structure
The repository consists of the following files/folders:
1. `main_actual.py`: The top-level file that runs the code for the practicals.
2. `main_testset.py`: The top-level file that runs the code for the practicals (for test dataset).
3. `test.py`: The unittest file that tests the correctness of the code.
4. `source_exclusion.py`: The script for visualizing sources of exclusion. I.e., if the entry-target pair is excluded because it is in the ventricles or vessels, or because it is too shear the cortex.
5. `src/`: Folder containing code for the practicals.
6. `week2/data/`: Folder containing data for the practicals.

## Usage
To run the main path planing script, simply run the ```python main_actual.py``` file.
For run with test dataset, run ```python main_testset.py```
For inspecting the source of exclusion, run ```python source_exclusion.py```
For unittest, run ```python test.py```

## Requirements
This code was written using Python 3.9.10. It also requires the libraries in requirements.txt
```pip install -r requirements.txt```

## What has been done
[x] This algorithm should take in a set of straight trajectories, represented as a pair of 3D Slicer Annotations (3D points), and two binary image volumes representing the critical structures and target structure. 
[x] It should return a single 3D Slicer Annotation representing the selected final trajectory(entry and target point). 
[x] To select the final trajectory the algorithm should select trajectories that meet the following hard constraints 
    [x] (a) avoidance of a critical structure
    [x] (b) placement of the tool into a target structure
    [x] (c) ensuring the trajectory is below a certain length. (unittested but commented out as the threshold is not specified)
[] The algorithm should then select an optimal trajectory based on maximizing distance to the critical structure. (not done)

## Visual
[Dash](assets/demo.png)
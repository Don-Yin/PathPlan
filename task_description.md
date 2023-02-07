# Task 0.
    a.	Load all the files located in the TestSet.
    i. What are the dimensions of the image
    ii. What are the number of points in the entries and targets fiducials
    d. Repeat these tasks for the files in BrainParcellation. Note how the sizes differ.

# Task 1. Given the following statements, write a corresponding formal mathematical test
    a. Placement of an electrode for recording temporal lobe epilepsy must target the hippocampus (r_hippo.nii.gz)
    b. Placement must avoid penetrating the ventricles (ventricles.nii.gz) to prevent cerebrospinal fluid leakage.
    c. Placement must avoid hitting any blood vessels (vessels.nii.gz) to prevent haemorrhage.
    d. Electrodes may deflect if not perpendicular (<55°; should be above 55) to cortex (cortex.nii.gz) upon entry. I.E. tool placement should be placed similar to green trajectory, the orange trajectory is too shear:
    (write down the mathematical test for each of the above statements)

# Task 2. 
    For each mathematical test in Task 1 design a simple algorithm on paper that can perform the check. First identifying the input and output datatypes and then determining how the information should flow through the program to give the desired output. Determine its Big O Notation
    (come up with the algorithm and then determine its Big O notation)

# Task 3. For each algorithm in Task 2, write a python function in 3D Slicer.
    a.	Use the Extension Wizard found under “Developer Tools” to create your own module (I suggest naming it “PathPlanning”).
    b.	Open the file in your favourite python editor and identify
        i.	Where the portions of the code related to its layout on the screen are
        ii.	Where the functions within the module are
        iii.	Where the test call is
    c.	For each algorithm create a new function to perform the given task.
    d.	Determine its Big O notation – is this the same as Task 2. If not, what identify the changes made to the algorithm and why.
    e.	Evaluate how long each algorithm takes. This can be done with the following code
    f.	Determine how many trajectories can be rejected for each test out of the total number of points
    (actually implement the algorithms in python)

# Task 4. 
    Based on the Task 3 identify the order of operations each test should run, provide a justification based on theoretical and practical (time and search space reduction) considerations. Implement the end-to-end algorithm; report on the final runtime performance. Note this should be faster than the summative test in Task 3.
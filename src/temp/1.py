import SimpleITK as sitk
from pathlib import Path
import os
import pandas
from io import StringIO
import vtk
from vtk import vtkImageAccumulate
import faulthandler

faulthandler.enable()


# Load the brain.nii.gz image
import SimpleITK as sitk
from pprint import pprint


# Load the image
image_1 = sitk.ReadImage("brain.nii.gz")
image_2 = sitk.ReadImage("fakeBrain.nii.gz")


def segment_brain(image):
    # Threshold the image
    threshold_filter = sitk.ThresholdImageFilter()
    threshold_filter.SetLower(100)
    threshold_filter.SetUpper(200)
    threshold_filter.SetOutsideValue(0)

    # Erode the image
    erode_filter = sitk.BinaryErodeImageFilter()
    erode_filter.SetKernelRadius(2)
    erode_filter.SetForegroundValue(1)

    # Dilate the image
    dilate_filter = sitk.BinaryDilateImageFilter()
    dilate_filter.SetKernelRadius(2)
    dilate_filter.SetForegroundValue(1)

    image = threshold_filter.Execute(image)
    image = erode_filter.Execute(image)
    image = dilate_filter.Execute(image)

    # Display the segmented brain
    sitk.Show(image, "Segmented Brain 1")

    return image


def segment_brain_2(image):
    array = sitk.GetArrayFromImage(image)


def image_threshold(image):
    # Create a threshold filter
    threshold_filter = sitk.ThresholdImageFilter()
    # Set the lower and upper threshold
    threshold_filter.SetLower(100)
    threshold_filter.SetUpper(200)
    # Apply the filter
    image_threshold = threshold_filter.Execute(image)
    # visualize
    sitk.Show(image_threshold)


def itk_to_vtk(sitk_image):
    # Convert SimpleITK image to NumPy array
    np_image = sitk.GetArrayFromImage(sitk_image)

    # Convert NumPy array to VTK image
    vtk_image = vtk.vtkImageData()
    vtk_image.SetDimensions(np_image.shape)
    vtk_image.AllocateScalars(vtk.VTK_FLOAT, 1)
    vtk_image.GetPointData().GetScalars().SetVoidArray(np_image, np_image.nbytes, 1)

    return vtk_image


def make_marching_cubes(vtk_image, level=0.5):
    # level is the threshold; anything below is set to background and above is set to foreground
    # so for a binary image, level=0.5 should be fine
    # for a greyscale image, you might want to try higher values
    # Create a marching cubes filter
    # print(vtk_image.GetDimensions())
    marching_cubes = vtk.vtkDiscreteMarchingCubes()
    marching_cubes.SetInputData(vtk_image)
    marching_cubes.SetValue(1, level)
    marching_cubes.Update()

    image_accumulate = vtkImageAccumulate()
    image_accumulate.SetInputData(vtk_image)
    image_accumulate.Update()

    # print(image_accumulate.GetMax())

    return marching_cubes.GetOutput()


def render_vtk(vtk_image):
    # Create a renderer
    renderer = vtk.vtkRenderer()

    # Create a render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Create an interactor
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Create a volume mapper
    volume_mapper = vtk.vtkSmartVolumeMapper()
    volume_mapper.SetInputData(vtk_image)

    # Create a volume property
    volume_property = vtk.vtkVolumeProperty()

    # Create a volume
    volume = vtk.vtkVolume()
    volume.SetMapper(volume_mapper)
    volume.SetProperty(volume_property)

    # Add the volume to the renderer
    renderer.AddViewProp(volume)

    # Set the background color
    renderer.SetBackground(0.2, 0.2, 0.2)

    # Render the image
    render_window.Render()

    # Start the interactor
    interactor.Start()


class Fcsv:
    def __init__(self, path_fcsv):
        self.path_fcsv = path_fcsv

        self.parse_fcsv()

    def parse_fcsv(self):
        with open(self.path_fcsv, "r") as loader:
            data = loader.read()

        data = data.splitlines()
        entries = [i for i in data if i.startswith("#")]
        entries = [i.replace("# ", "") for i in entries]
        content = [i for i in data if not i.startswith("#")]

        content = StringIO("\n".join(content))
        content_df = pandas.read_csv(content, sep=",")

        columns = [i for i in entries if i.startswith("columns")][0].replace("columns = ", "").split(",")

        # add columns to content_df
        content_df.columns = columns

        self.entries = entries
        self.content_df = content_df


if __name__ == "__main__":

    # a.	Load all the files located in the TestSet.
    # b.	In the python console use slicer.util to assign a variable to each node
    test_images = Path("week-2", "practicals", "TestSet").glob("*.nii.gz")
    test_images_itk = [sitk.ReadImage(i) for i in test_images]

    # c.	Identify the size of the data in each node.
    #     i.	What are the dimensions of the image
    dimensions = [i.GetSize() for i in test_images_itk]

    #     ii.	What are the number of points in the entries and targets fiducials
    num_points_entries = Fcsv(Path("week-2", "practicals", "entries.fcsv")).content_df.shape[0]
    num_points_targets = Fcsv(Path("week-2", "practicals", "targets.fcsv")).content_df.shape[0]

    print(f"Number of points in entries: {num_points_entries}")
    print(f"Number of points in targets: {num_points_targets}")

    #     iii.	For the binary images – use the convert label map to segmentation node (as shown below) to create a surface node. What is the bounding box of each surface node.
    #     iv.	Try to identify a way to convert a label map to a segmentation node from the command prompt.

    test_images_vtk = [itk_to_vtk(i) for i in test_images_itk]
    image_marching_cubes = [make_marching_cubes(i) for i in test_images_vtk]

    # render_vtk(i)

    # for i in image_marching_cubes:
    #     print(i.GetNumberOfPolys())

    # d.	Repeat these tasks for the files in BrainParcellation. Note how the sizes differ.
    brain_images = Path("week-2", "practicals", "BrainParcellation").glob("*.nii.gz")
    brain_images_itk = [sitk.ReadImage(i) for i in brain_images]

    for brain_image in brain_images_itk:
        print(brain_image)
        # print the data as a numpy array
        print(sitk.GetArrayFromImage(brain_image))

    brain_images_vtk = [itk_to_vtk(i) for i in brain_images_itk]

    print(f"Number of images in BrainParcellation: {len(brain_images_itk)}")

    from random import shuffle

    shuffle(brain_images_vtk)

    brain_image_marching_cubes = [make_marching_cubes(i) for i in brain_images_vtk]

    for i in brain_image_marching_cubes:
        print(i.GetNumberOfPolys())

    print(f"Number of images in BrainParcellation: {len(brain_images_itk)}")

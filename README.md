# BrainSeg

Project of automatic brain segmentation using Deep Learning.

## Installation

Get a linux environment and open the terminal. 
On windows, you can use the Windows Subsystem for Linux (WSL) 
If you are using Ubuntu, you can use `Ctrl + Alt + T`

The installation of the BrainSeg can be done using the `./install.sh` command.
It will require poetry, and install the full environment.

## Get Connectome Workbench
To explore the MRI data interactively, you'll need to install the Connectome Workbench application :
```bash 
wget https://www.humanconnectome.org/storage/app/media/workbench/workbench-linux64-v2.0.1.zip
```
You need to install the unzip package : 
```bash
sudo apt install unzip
```
And then unzip it : 
```bash 
unzip workbench-linux64-v2.0.1.zip
```
Install the dependencies : 
```bash
sudo apt install libglu1 libx11-6 libxext6 libxi6 libstdc++6 libgcc-s1 libgomp1
```


# Performing Histology to MRI mapping of neurons

## Preprocessing 
What needed : 
- Histological sections brain as .czi files
- Histological sections exported from .czi as .jpg with 10x downscale
- Individual MRI file, you can eventually use template MRI
- Plotted cell files as .svg (from CellPlot V1.003) or as .geojson (from QuPath 5.3.0)

## Configuration files
Each case is controlled by a dedicated configuration file that defines all necessary parameters.
These parameters are grouped into six main categories : 
- **Manual parameters**: Values that mus be calculated and provided manually
- **Root**: Root paths specific to the current case or dataset
- **Technical parameters**: Physical or acquisition-related settings
- **Data Input**: Filenames or masks required as input for the pipeline
- **Architechture**: Directory stucture difning where input data is located
- **Environment**: Specific environment variables, such as paths to model weights or executable binaries

## Mandatory parameters 
Most parameters are specific to one or few scripts, but some are alward mandatory. The list is as follow :
- `start` : the first slice index
- `end` : the last slice index
- `step` : usually 1

## Command Names
All the commands from the BrainSeg pipeline are run from its repository which is located in ~/pipeline/Brainseg. From there, most commands are run with the following line : 
`./run.sh <command> path_to_your_config_file.ini`


## Full Process

### 1) Segmentation of histological sections
The segmentation step consists of semi-automatically outlining the white matter and cortical regions in the histological sections, using QuPath.

To compute the `segmentation`, you will need the following variables :
- `slides_dir`
- `slides_mask`
- `segmentation_weights (h5 file)`
- `annotation_dir`
- `annotation_mask`

To ensure the segmentation process went fine, you should check either the *geojson* file opened with their corresponding slide on QuPath, or directly assess the segmentation quality of the png images *(wm and pial)*.
In case of failure, it is advised to manually draw 10 slices evenly distributed throughout the brain. You can then retrain the segmentation model.

### 2) Retraining the segmentation model

### 3) Merge cells based on the performed segmentation
The segmentation results can be merged with external annotation plots though two distinct steps, depending on the tool used to generate the plots.
- If the plots were created using PlotFast/CellPlot, use the corresponding merging step designed for this format.
- If the plots were created with QuPath, follow the the alternative merging step tailored to QuPath outputs.

These steps ensure proper alignment between the segmentation masks and the annotated sections, regardless of the software originally used.

To compute the `merge` fluorescent sections from Cellplot, you will need :
- Having run the segmentation before
- Mandatory parameters
- `plotfast_dir`
- `plotfast_mask`
- `annotations_dir`
- `full_annotations_mask`
- `merged_annotations_mask`

### 4) Selecting the cutting angle of the brain
### 5) Making the MRI sections
### 6) Creating transforms between Histology and MRI
### 7) Creating some necessary intermediate MRI files
### 8) Transfer the neurons onto the MRI surface and Extract connectivity values



# Process

The segmentation is a two-step process : training and application.

### Training

The data must be first preprocessed

### Application

Run the command apply.sh --data `data_dir`

## Data

The directory containing the input data must generally be specified 
using `--data`. The directory must contain a `slides` folder and a
`annotations` folder. The annotation must be an image of png format.

The ratio of the annotation dimensions must be equal to the ratio of the side dimensions, 
but the size in itself may be different.


# Full process

0) Have a folder of slides from an individual, named `SLIDE_FOLDER`
1) Use PlotFast to trace the contour and export the file as svg 
using the Ctrl + E shortcut. 
The svg files are located in the `SVG_FOLDER`. The svg stem name must be
similar to the one of the slide + the "seg" suffix.
2) The svg files must be preprocessed and converted to png in order to form
a proper mask dataset in a folder `FULL_MASK_FOLDER`. The `full_prepro_svg.py`
command is used to generate that folder.
3) These png files must be manually filled using paint on a Windows computer.
4) [Optional] After, if not all masks are filled,
the filled masks are moved to a `FILLED_MASK_FOLDER`.
5) Use the command `generate_image_dataset.py` that uses the `SLIDE_FOLDER`,
the `FILLED_MASK_FOLDER` and generates a `CURATION_DATASET_FOLDER`.
6) Use the streamlit app using `poetry run streamlit run main_streamlit.py`
Click on 001 to exclude the image and higher scores according to the
mask quality
7) Train a model using a notebook (a script is waiting to be done)
8) Use `apply.sh` to apply a model on a whole slide, this will generate
a png file
9) Use `convert_png_svg.py` to convert png back to svg. You can also use
another svg as template, predictions will be added to it (in a new file).


# Updates

A v2 version of most of the files contains a version handling
bi-resolution segmentation. This is because single resolution segmentation
appeared to be less efficient.

# Multi-Resolution process

1) Considered a slide folder and a mask folder (built as described
in the previous "full process")
2) We must generate the dataset using the descriptors with the command 
`generate_descriptor_dataset.py` that requires the output folder and
the list of structures (e.g. white matter, claustrum etc) 
(Now its `DataGenerator3L.ipynb`)
3) Run `train_multiresolution.py` with the same parameters as for the
dataset generation and providing the output of the model
4) Run `apply_multiresolution.py` with the output of the model
on your slide (or slide directory)
5) Run `converter.py` to convert the output mask to a processed
json or svg file.
6) Run `merge_json.py` to merge multiple json files after an affine
registration step on the outline
7) Your file is normally ready to be imported directly into QuPath
8) You can run 4/5/6 in once using `process_slides.py` and providing
the folder of the slides and the folder of the other GeoJSON files

## Dev Advancement

1) Done
2) Can be done quickly (just need to convert DataGenerator3L.ipynb
to python script and parametrize it)
3) Can be done quickly, ipynb conversion + parametrization, but after
a validation of the efficiency of the model
4) An update of apply_v4.py changing the model and the data pipeline
(normally few changes are required)
5) Same conversion as before for the polygon / polylines, but this
time with more processing for wm border (requires a samples to be made)
6) Tricky part has been de-risked, now just need to implement 
(and verify that outline conversion to raster is easy) /!\ we also
need to find the coordinate system of qupath


## Test data

Where can I find them ?

SLIDE="/media/`whoami`/LaCie/REGISTRATION_PROJECT/
M148_RH/M148 LHRH324.czi"

WEIGHTS="/media/`whoami`/LaCie/Data/models/trires/
model_test_v1_e7_iou0.897.h5"

OUTPUT="/media/`whoami`/LaCie/REGISTRATION_PROJECT/
GENERATED_MASKS_PNG/qupath_version1"

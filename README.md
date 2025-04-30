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

## Command Names
All the commands from the BrainSeg pipeline are run from its repository which is located in ~/pipeline/Brainseg. From there, most commands are run with the following line : 
`./run.sh <command> path_to_your_config_file.ini`


## Full Process

### 1) Segmentation of histological sections
The segmentation step consists of semi-automatically outlining the white matter and cortical regions in the histological sections, using QuPath.

To compute the segmentation, you will need the following variables 


### 2) Merge cells based on the performed segmentation
### 3) Selecting the cutting angle of the brain
### 4) Making the MRI sections
### 5) Creating transforms between Histology and MRI
### 6) Creating some necessary intermediate MRI files
### 7) Transfer the neurons onto the MRI surface and Extract connectivity values




### Application

Run the command apply.sh --data `data_dir`

## Data

The directory containing the input data must generally be specified 
using `--data`. The directory must contain a `slides` folder and a
`annotations` folder. The annotation must be an image of png format.

The ratio of the annotation dimensions must be equal to the ratio of the side dimensions, 
but the size in itself may be different.



## Pipeline supplementary information

section_id = translation + (scale * mri_id)
mri_id = (section_id - translation) / scale

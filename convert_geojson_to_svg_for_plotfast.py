"""
TODO :
- Load the svg file
- Get the "outline" polygon
- For each svg geometry, create the geojson equivalent (how ?)
- transfer coordinates


To create the json equivalent :
- List all relevant information to keep (more than the geometry) => color (type), point cat
- Build the mapping if required => a starting point is in `prepro_svg.py`
- Create the json with the mapped metadata
"""
import os
from pathlib import Path
import argparse
import numpy as np
from geojson import load, FeatureCollection, dump, utils
import matplotlib
from tqdm import tqdm

from brainseg.geo import svg_to_geojson, simplify_line, simplify_all
from brainseg.registration import get_affine_transform_matrix
from brainseg.viz.draw import draw_polygon_border, draw_in_mask

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import lxml.etree as et

from brainseg.config import fill_with_config
from brainseg.path import build_path_histo
from brainseg.svg.utils import is_polygon, css_to_dict, points_to_numpy, get_svg_root_plotfast
from brainseg.utils import flatten

# this is not good practice
# sys.path.insert(0, str(Path(__file__).parent / "../build/SimpleITK-build/Wrapping/Python/"))

DICT_COLOR_TO_AREA = {
    "rgb(255,0,0)": "outline",
    "rgb(243,0,0)": "claustrum",
    "rgb(228,0,0)": "putamen",
    "rgb(0,248,255)": "white_matter",
    "rgb(0,255,255)": "layer_4",
}


def extract_outline_svg(svg):
    # we assume there is only one outline
    for x in svg.iterchildren():
        if not is_polygon(x):
            continue
        css = x.attrib["style"]
        d = css_to_dict(css)
        if d.get("stroke") == "rgb(255,0,0)":
            p = points_to_numpy(x.attrib["points"])  # TODO need somewhere to shift by 30000, 30000
            print(p.shape, p.min(axis=0), p.max(axis=0))
            return p

    raise IndexError("No outline found in the svg !")


def get_classification_name(obj):
    try:
        name = obj["properties"]["classification"]["name"]
    except (IndexError, KeyError):
        name = None
    return name


def run(geo_path):
    with open(geo_path, "r") as f:
        geo_cv = load(f)

    root = get_svg_root_plotfast()

    for feat in geo_cv["features"]:
        print(feat)
        if feat["geometry"]["type"] == "Polygon":
            pass
        pass  # transform it as a svg element


def main(args):
    for filename in os.listdir(args.dir):
        if filename.endswith(".geojson"):
            run(args.dir / filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", type=Path)

    args_ = parser.parse_args()

    main(args_)

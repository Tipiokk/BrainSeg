import argparse
from pathlib import Path

import geojson
from shapely.affinity import scale
import geopandas as gpd

from brainseg.geo import quickfix_multipolygon_qupath


def rescale_polygon(polygon, scale_factor):
    rescaled_polygon = scale(polygon, xfact=scale_factor, yfact=scale_factor, origin=(0, 0))
    return rescaled_polygon


def main(args):
    gdf = gpd.read_file(args.geojson)
    gdf["geometry"] = gdf["geometry"].apply(lambda x: rescale_polygon(x, args.scale))
    geo = geojson.FeatureCollection(
        [geojson.Feature(geometry=row['geometry'].__geo_interface__, properties=row.drop('geometry').to_dict())
         for _, row in gdf.iterrows()]
    )

    geo = quickfix_multipolygon_qupath(geo)

    # Step 2: Save as a GeoJSON file
    with open(args.geojson, "w") as f:
        geojson.dump(geo, f)
    # gdf.to_file(args.geojson, driver="GeoJSON")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--geojson", type=Path)
    parser.add_argument("-s", "--scale", type=float)
    args_ = parser.parse_args()
    main(args_)

import argparse
from pathlib import Path

import geojson
from shapely.affinity import scale
import geopandas as gpd

from brainseg.geo import quickfix_multipolygon_qupath
from brainseg.polygon import translate_polygon, rescale_polygon


def main(args):
    gdf = gpd.read_file(args.geojson)
    gdf["geometry"] = gdf["geometry"].apply(lambda x: translate_polygon(x, x=-args.center_x, y=-args.center_y))
    gdf["geometry"] = gdf["geometry"].apply(lambda x: rescale_polygon(x, args.scale))
    gdf["geometry"] = gdf["geometry"].apply(lambda x: translate_polygon(x, x=args.center_x, y=args.center_y))
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
    parser.add_argument("-x", "--center_x", type=float, default=0.0)
    parser.add_argument("-y", "--center_y", type=float, default=0.0)
    args_ = parser.parse_args()
    main(args_)

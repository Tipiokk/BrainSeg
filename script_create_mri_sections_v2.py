import argparse
import os
from pathlib import Path
import numpy as np
import subprocess
import configparser
import tqdm

from brainseg.config import fill_with_config
from brainseg.misc.convert_space import build_coord_from_param
from brainseg.utils import hash_mri_window, write_txt


def get_values_from_wb(ox, oy, oz, slice_number, top=28, bottom=-22, left=-32, right=32):
    pixel2mm = build_coord_from_param(ox, oy, oz, slice_number,
                                      top=top, bottom=bottom, left=left, right=right
                                      )

    blmm = pixel2mm.T @ np.array([1, 1000, 1])
    brmm = pixel2mm.T @ np.array([1000, 1000, 1])
    tlmm = pixel2mm.T @ np.array([1, 1, 1])

    print(blmm, brmm, tlmm)

    values = list(np.concatenate([blmm, brmm, tlmm]))
    text = " ".join(map(lambda x: f"{x:.2f}", values))
    return text


def main(args):
    d_outputs = dict(
        gm="ribbon_both_GM.nii.gz",
        wm="ribbon_both_WM.nii.gz",
        pial="ribbon_both_PIAL.nii.gz",
        raw="T1w_acpc_dc_restore.nii.gz",
    )
    for i in tqdm.tqdm(np.arange(args.start, args.end, args.step)):
        i_mri = (i - args.translation_y) / args.scale_y
        i_histo = str(int(i)).zfill(3)
        coord_values = get_values_from_wb(args.angle_x, 0, args.angle_z, i_mri,
                                          top=args.mri_window[0], bottom=args.mri_window[1],
                                          left=args.mri_window[2], right=args.mri_window[3])
        for ftype, fname in d_outputs.items():
            output_path = args.mri_sections_dir / f"{ftype}_{i_histo}.png"
            write_txt(args.mri_sections_dir / f"hash_{ftype}_{i_histo}.txt", hash_mri_window(args.mri_window))

            volume_name = args.mri_dir / fname
            raw_cmd = args.wb_binary
            max_val = 400 if ftype == "raw" else 1  # empirical 400
            cmd = f'{raw_cmd} -volume-capture-plane "{volume_name}" 1 TRILINEAR 1000 1000 ' \
                  f'0 {max_val} {coord_values} "{output_path}"'
            # print(cmd.split(" "))
            os.system(cmd)
            # subprocess.check_output(cmd.split(" "))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mri_dir", type=Path, default=None)
    parser.add_argument("-c", "--config", type=Path, default=None)
    parser.add_argument("-x", "--angle_x", type=float, default=None)
    parser.add_argument("-z", "--angle_z", type=float, default=None)
    parser.add_argument("--translation_y", type=float, default=None)
    parser.add_argument("--scale_y", type=float, default=None)
    parser.add_argument("--mri_window", type=str, default=None)
    parser.add_argument("--start", type=float, default=None)
    parser.add_argument("--end", type=float, default=None)
    parser.add_argument("--step", type=float, default=None)
    parser.add_argument("-o", "--mri_sections_dir", type=Path, default=None)
    parser.add_argument("-b", "--wb_binary", type=Path, help="The path to the `wb_command` binary", default=None)
    args_ = fill_with_config(parser)
    args_.mri_sections_dir.mkdir(parents=True, exist_ok=True)
    args_.mri_window = list(map(float, args_.mri_window.split(",")))
    main(args_)

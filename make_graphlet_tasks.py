#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path

from toolbox import listfile

grafene = (Path(__file__).parent / "compute_grafene_features.py").resolve().absolute()
orca    = (Path(__file__).parent / "compute_orca_graphlets.py").resolve().absolute()

mode2script = {'orca': orca, 'grafene': grafene}

def arguments():
    parser = argparse.ArgumentParser(description="generate disBatch taskfile for graphlets")
    parser.add_argument("listfile", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("-mode", choices=['grafene', 'orca'], default='orca')
    parser.add_argument("-t", type=int, default=6, help="Contact map threshold")
    return parser.parse_args()



if __name__ == '__main__':
    args = arguments()
    
    script = mode2script[args.mode]
    threshold = args.t

    command_formatter = (f"python {script} ""{input_file} {output_file} "f"-t {threshold}").format
    
    inlist = listfile.read(args.listfile)

    args.output_dir.mkdir(exist_ok=True, parents=True)

    for input_file in map(Path, inlist):
        output_file = args.output_dir / f"{input_file.stem}.npz"
        cmd = command_formatter(input_file=input_file, output_file=output_file)
        print(cmd)



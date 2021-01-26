#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path

from toolbox import listfile

script = ( Path(__file__).parent / "count_graphlets.py" ).resolve().absolute()

def arguments():
    parser = argparse.ArgumentParser(description="generate disBatch taskfile for graphlets")
    parser.add_argument("listfile", type=Path, help="List of IDs")
    parser.add_argument("input_dir", type=Path, help="Directory to look for IDs")
    parser.add_argument("output_dir", type=Path, help="Directory to place individual files")
    parser.add_argument("-mode", choices=['grafene', 'orca'], default='orca')
    parser.add_argument("-t", type=int, default=6, help="Contact map threshold")
    return parser.parse_args()

if __name__ == '__main__':
    args = arguments()
    
    mode = args.mode
    threshold = args.t

    command_formatter = (f"python {script} ""{input_file} {output_file} "f"-t {threshold} -mode {mode}").format
    
    inlist = listfile.read(args.listfile)

    args.output_dir.mkdir(exist_ok=True, parents=True)

    for ID in inlist:
        input_file  = args.input_dir / f"{ID}.pt"
        output_file = args.output_dir / f"{ID}.npz"
        cmd = command_formatter(input_file=input_file, output_file=output_file)
        print(cmd)



#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
from pathlib import Path

import torch
import numpy as np

from graphlet_helper import ORCARunner, GRAFENERunner

modemaker = {'orca': ORCARunner, 'grafene': GRAFENERunner}

def check_exists(filename):
    filename = Path(filename)
    if not filename.exists():
        raise FileNotFoundError(f"Can\'t find {filename}")
    return filename

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calculate graphlets")
    parser.add_argument("input_pt", type=check_exists,
                        help="Input coordinate or distance map file (inferred based on shape)")
    parser.add_argument("output_npz", type=Path,
                        help="Output features")
    parser.add_argument("-t","--threshold", type=int,
                        help="Contact map threshold", default=10, dest='threshold')
    parser.add_argument("-mode", choices=['orca', 'grafene'])

    args = parser.parse_args()
    
    print(f"input file: {args.input_pt}")
    print(f"output file: {args.output_npz}")
    print(f"t={args.threshold}, mode={args.mode}") 
    runner = modemaker[args.mode](args.threshold)
   
    infile   = args.input_pt    
    outfile  = args.output_npz

    result = runner.run(infile)
    print("Saving now") 
    np.savez_compressed(outfile, **result)
    print("complete")

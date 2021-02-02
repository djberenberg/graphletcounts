#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extract global graphlet degree vectors
"""

import argparse
from pathlib import Path
import numpy as np

from graphlet_helper.toolbox import listfile

def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("listfile", type=Path, help="Domain list")
    parser.add_argument("input_dir", type=Path, help="Input directory")
    parser.add_argument("--output-npz", type=Path, help="final npz output path")
    return parser.parse_args()

def get_shape(filename):
    data = np.load(filename)
    mat = data['mat']
    
    nc, d = mat.shape
    return nc, d

if __name__ == '__main__':
    args = arguments()
    
    output_npz = args.output_npz
    if output_npz is None:
        output_npz = f"{args.input_dir.stem}.npz" 

    proteins = listfile.read(args.listfile)
    
    N = len(proteins)
    nc, d = get_shape(args.input_dir / f"{proteins[0]}.npz")
        
    final = np.zeros((nc, N, d))
    for i, protein in enumerate(proteins):
        npz = args.input_dir / f"{protein}.npz"
        data = np.load(npz)
        gdv = data['mat']
        channels = data['channels']

        for channel in range(nc):
            final[channel, i, :] = gdv[channel, :]

        print(f"\r{80 * ' '}\rfilling ({i}/{N}, {d}) graphlet count mat", end='', flush=True)

    print(f"\nSaving to {args.output_npz}")
    np.savez_compressed(output_npz, proteins=proteins, channels=channels, mat=final)


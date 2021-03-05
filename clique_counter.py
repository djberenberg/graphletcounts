#!/usr/bin/env python

import argparse
from pathlib import Path

import numpy as np

from graphlet_helper import CliqueRunner
from graphlet_helper.toolbox import listfile

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count cliques")
    parser.add_argument("listfile", type=Path)
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_npz", type=Path)
    parser.add_argument("-t", type=int, help="Threshold")
    parser.add_argument("--quiet", "-q", dest="quiet", action='store_true', default=False)
    
    args = parser.parse_args()

    proteins = listfile.read( args.listfile )
    N = len(proteins)
    
    runner = CliqueRunner(args.t)

    output_npz = args.output_npz
    if output_npz is None:
        output_npz = f"{args.input_dir.stem}.npz" 
   
    nc = 2
    mat = None
    for i, protein in enumerate(proteins):
        try:
            result = runner.run(args.input_dir / f"{protein}.pt")
        except FileNotFoundError:
            continue
        features = result['mat']
        if mat is None:
            nc, d = features.shape

            shape = (nc, N, d)
            mat = np.zeros(shape)
            channels = result['channels']

        for channel in range(nc):
            mat[channel, i, :] = features[channel, :]
        
        if not args.quiet:
            print(f"\r{80 * ' '}\rfilling ({i}/{N}, {d}) graphlet count mat", end='', flush=True)

    print(f"\nSaving clique distributions to {output_npz}")

    np.savez_compressed(output_npz, proteins=proteins, channels=channels, mat=mat)

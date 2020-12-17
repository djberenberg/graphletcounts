#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extract global graphlet degree vectors
"""

import csv
import argparse
from pathlib import Path
import numpy as np

from toolbox import listfile

def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("npzlist", type=Path, help="Listfile of npzs")
    parser.add_argument("output_npz", type=Path, help="final npz output path")
    parser.add_argument("output_tsv", type=Path, help="output tsv with timing info")
    return parser.parse_args()


if __name__ == '__main__':
    args = arguments()

    input_npzs = sorted(map(Path, listfile.read(args.npzlist)))
    protein_keys = list(map(lambda pth: pth.name.replace("".join(pth.suffixes), ""), input_npzs))
    
    npz = np.load(input_npzs[0])
    raw_gdv = npz['graph_gdvs'][0, :]
    normed_gdv = npz['graph_gdvs'][1, :]

    l = len(input_npzs)
    w = raw_gdv.shape[0]

    final_mat = np.zeros((2, l, w))
    final_mat[0, 0, :] = raw_gdv 
    final_mat[1, 0, :] = normed_gdv

    channels = npz['channels']


    with open(args.output_tsv, 'w') as tsvfile:
        writer = csv.DictWriter(tsvfile, delimiter='\t', fieldnames=['prot_id', 'length', 'elapsed'])
        for i, npz_path in enumerate(input_npzs[1:], 1):
            npz = np.load(npz_path, allow_pickle=True)
            final_mat[0, i, :] = npz['graph_gdvs'][0, :]
            final_mat[1, i, :] = npz['graph_gdvs'][1, :]

            prot_id = protein_keys[i]
            _, _, elapsed = npz['timing']
            if 'node_GDV' in npz.files:
                length = npz['node_GDV'].shape[0]
            elif 'length' in npz.files:
                length = npz['length']

            row = dict(prot_id=prot_id, length=length, elapsed=elapsed)
            writer.writerow(row)

            print(f"\r{80 * ' '}\rfilling ({i}/{l}, {w}) graphlet count mat", end='', flush=True)
    print("\r{80 * ' '}\rdone filling")

    #normed_mat = mat / mat.sum(axis=1)[:, None]
    
    #final_mat = np.concatenate([normed_mat[None, :, :], mat[None, :, :]])
    print(f"Saving to {args.output_npz}")
    np.savez_compressed(args.output_npz, proteins=protein_keys, channels=channels, features=final_mat)

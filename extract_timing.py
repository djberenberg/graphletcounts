#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extracts timing information from a collection of graphlets

Basically just a table of id, length, and elapsed compute time
"""

import csv
import argparse
from pathlib import Path

import numpy as np

from toolbox import listfile

def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("npzlist", type=Path, help="Listfile of npzs")
    parser.add_argument("output_tsv", type=Path, help="final tsv output path")
    return parser.parse_args()

if __name__ == '__main__':
    args = arguments()

    input_npzs = sorted(map(Path, listfile.read(args.npzlist)))
    protein_keys = list(map(lambda pth: pth.name.replace("".join(pth.suffixes), ""), input_npzs))
    
    l = len(input_npzs)
    print(f"Writing to {args.output_tsv}")
    with open(args.output_tsv, 'w') as tsv:
        writer = csv.DictWriter(tsv, delimiter='\t', fieldnames=['prot_id', 'length', 'elapsed'])
        writer.writeheader() 
        for i, (npz_path, prot_id) in enumerate(zip(input_npzs, protein_keys), 1):
            npz  = np.load(npz_path, allow_pickle=True)
            _, _, elapsed = npz['timing']
            if 'node_GDV' in npz.files:
                length = npz['node_GDV'].shape[0]
            elif 'length' in npz.files:
                length = npz['length']

            row = dict(prot_id=prot_id, length=length, elapsed=elapsed)
            writer.writerow(row)
            print(f"\r{80 * ' '}\r{i}/{l} rows written", end='', flush=True)
    print("\r{80 * ' '}\rdone")
        

# graphletcounts
Wrappers and scripts for counting (protein structure) graphlets. For calculating graphlets at scale, we have been parallelizing via <a href="https://github.com/flatironinstitute/disBatch">DisBatch</a>.

# Installation
```bash
python3 -m venv venv
git clone https://github.com/djberenberg/graphletcounts
source venv/bin/activate

pip install numpy scipy networkx torch
```

# Scripts
- `count_graphlets.py` - count graphlets (either via ORCA or GRAFENE) for an individual sample
```
usage: count_graphlets.py [-h] [-t THRESHOLD] [-mode {orca,grafene}]
                          input_pt output_npz

Calculate graphlets

positional arguments:
  input_pt              Input coordinate or distance map file (inferred based
                        on shape)
  output_npz            Output features

optional arguments:
  -h, --help            show this help message and exit
  -t THRESHOLD, --threshold THRESHOLD
                        Contact map threshold
  -mode {orca,grafene}
```

- `reduce_graphlets.py` - compress a list of individual graplhet files to one single matrix
```
usage: reduce_graphlets.py [-h] [--output-npz OUTPUT_NPZ] listfile input_dir

Extract global graphlet degree vectors

positional arguments:
  listfile              Domain list
  input_dir             Input directory

optional arguments:
  -h, --help            show this help message and exit
  --output-npz OUTPUT_NPZ
                        final npz output path
```

- `make_graphlet_tasks.py` - generates the DisBatch taskfile.
```
usage: make_graphlet_tasks.py [-h] [-mode {grafene,orca}] [-t T]
                              listfile input_dir output_dir

generate disBatch taskfile for graphlets

positional arguments:
  listfile              List of IDs
  input_dir             Directory to look for IDs
  output_dir            Directory to place individual files

optional arguments:
  -h, --help            show this help message and exit
  -mode {grafene,orca}
  -t T                  Contact map threshold
```

# More information
- Faisal, F.E., Newaz, K., Chaney, J.L. et al. GRAFENE: Graphlet-based alignment-free network approach integrates 3D structural and sequence (residue order) data to improve protein structural comparison. Sci Rep 7, 14890 (2017). https://doi.org/10.1038/s41598-017-14411-y

- More information given in
Tomaž Hočevar, Janez Demšar, A combinatorial approach to graphlet counting, 
Bioinformatics, Volume 30, Issue 4, 15 February 2014, Pages 559–565, https://doi.org/10.1093/bioinformatics/btt717

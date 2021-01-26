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
- `reduce_graphlets.py` - compress a list of individual graplhet files to one single matrix
- `make_graphlet_tasks.py` - generates the DisBatch taskfile.

# More information
- Faisal, F.E., Newaz, K., Chaney, J.L. et al. GRAFENE: Graphlet-based alignment-free network approach integrates 3D structural and sequence (residue order) data to improve protein structural comparison. Sci Rep 7, 14890 (2017). https://doi.org/10.1038/s41598-017-14411-y

- More information given in
Tomaž Hočevar, Janez Demšar, A combinatorial approach to graphlet counting, 
Bioinformatics, Volume 30, Issue 4, 15 February 2014, Pages 559–565, https://doi.org/10.1093/bioinformatics/btt717

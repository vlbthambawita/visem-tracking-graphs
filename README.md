# visem-tracking-graphs

# Sperm Video Graph Analysis

This repository contains code for creating and saving graphs from a sperm video dataset, where each sperm is represented by a node in the graph, and edges represent spatial and temporal relationships between the sperm. Spatial edges connect sperms within the same frame, while temporal edges connect sperms across different frames.

## Requirements

- Python 3.7 or higher
- NetworkX
- tqdm

To install these dependencies, run:

```bash
pip install networkx tqdm
```

## Usage
- Replace input_root_dir with the actual path to the root directory containing the sperm video dataset.
- Replace output_root_dir with the actual path to the root directory where you want to save the output graphs.
- Modify the spatial_thresholds list if you want to change the spatial thresholds for connecting nodes.
- Run the script, and the graphs will be saved to the specified output directory.

The script will create separate directories for each spatial threshold, and inside each directory, it will save frame graphs and the video graph as GraphML files.

Example
Replace input_root_dir and output_root_dir with the actual paths to the input and output directories, respectively, and run the script:

```python
python generate_graphs.py
```
The script will generate the graphs for each spatial threshold and save them to the output directory.



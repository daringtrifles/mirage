import h5py
import numpy as np

def print_hdf5_structure(name, obj):
    if isinstance(obj, h5py.Dataset):
        print(f'Dataset: {name}')
        print(f'  Shape: {obj.shape}')
        print(f'  Dtype: {obj.dtype}')
    elif isinstance(obj, h5py.Group):
        print(f'Group: {name}')

# Open the file
file_path = '/home/harshapolavaram/clean_code/sim_experiments/mirage/two_piece_assembly/image_84.hdf5'
with h5py.File(file_path, 'r') as f:
    print("\nHDF5 file structure:")
    print("===================")
    f.visititems(print_hdf5_structure) 
from pathlib import Path
import numpy as np
from scipy import stats
import pickle


# AT THIS POINT IN TIME:
# The script needs to act on an already existing Pickle file
# I am testing every unit (extracting, elaborating...) singularly
raw_dataset_path = Path(__file__).parent / 'data' / 'UH70-FS'
load_path = raw_dataset_path / 'iv_curves_UH70FS.pkl'

# The script simply creates a new pickle file (no overwriting)
save_path = raw_dataset_path / 'elaborated_UH70FS.pkl'


# LOW LEVEL: I am linearly fitting the entire data
# later: fit only forward/reverse sweep
# later: fit bias regions
def calc_resistance(voltages, currents):
    
    slope, intercept, r_value, _, _ = stats.linregress(voltages, currents)

    return {
        'resistance_ohm' : 1 / slope,
        'intercept' : intercept,
        'r_squared' : r_value**2,
    }


# Using numpy for simplicity, in the future the data might
# be directly be stored in numpy or even dataframes (pandas)
def compute_elaborations(dataset):
    V = np.array(dataset['curves']['Voltage'])
    I = np.array(dataset['curves']['Current'])
    
    return {
        'resistance_fit': calc_resistance(V, I),
        # add more later
    }

# The ** operator is cictionary unpacking.
# Takes all key-value pairs inside and places them
def add_elaborations(dataset):
    return {
        **dataset,
        'elaborations': compute_elaborations(dataset)
    }


def dump_data(save_path: Path, data: list[dict]):
    with open(save_path, 'wb') as f:
        pickle.dump(data, f)
    print(f"Saved {len(data)} curves to {save_path}")


def main():
    with open(load_path, 'rb') as f:
        datasets = pickle.load(f)

    processed_datasets = [add_elaborations(d) for d in datasets]

    dump_data(save_path, processed_datasets)


if __name__ == "__main__":
    main()
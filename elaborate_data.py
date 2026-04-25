from pathlib import Path
import numpy as np
from scipy import stats
import pickle


raw_dataset_path = Path(__file__).parent / 'data' / 'UH70-FS'
load_path = raw_dataset_path / 'iv_curves_UH70FS.pkl'
save_path = raw_dataset_path / 'elaborated_UH70FS.pkl'


def calc_resistance(voltages, currents):
    
    slope, intercept, r_value, _, _ = stats.linregress(voltages, currents)

    return {
        'resistance_ohm' : 1 / slope,
        'intercept' : intercept,
        'r_squared' : r_value**2,
    }


def compute_elaborations(dataset):
    V = np.array(dataset['curves']['Voltage'])
    I = np.array(dataset['curves']['Current'])
    
    return {
        'resistance_fit': calc_resistance(V, I),
        # add more later
    }


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
from pathlib import Path
import numpy as np
from scipy import stats
import pickle

# CONSTANTS
# METADATA: Information about the environment (Sample ID, Timestamp, P, T)
# contains geometric information on how the measurement was spatially performed 
# (Van Der Pauw alignement)
METADATA = "metadata" # container name
KEY_SAMPLE = "sample"
KEY_TIMESTAMP = "timestamp"
KEY_PRESSURE = "pressure_torr"
KEY_TEMPERATURE = "temperature_k"
KEY_GEOMETRY = 'alignment'
# DATA: Contains the arrays of measured values
DATA = "curves" # container name, could be more than 1 curve if Van Der Pauw
KEY_VOLTAGE = "Voltage"
KEY_CURRENT = "Current"
KEY_STD = "std_dev"
# ELABORATIONS: Contains the elaborations
ELABORATIONS = 'elaborations'
KEY_GLOBAL_LINEAR_FIT = 'global_linear_fit'


# AT THIS POINT:
# Working on an already created pickle (no raw TXT parsing here)
# Goal is to validate each step of the pipeline independently
dataset_dir = Path(__file__).parent / 'data' / 'UH70-FS'
pickle_curves_input = dataset_dir / 'iv_curves_UH70FS.pkl'

# Always write to a new file (avoid accidental overwrite of previous stages)
# This lets me keep intermediate versions while iterating
pickle_elaborations_output = dataset_dir / 'elaborated_UH70FS.pkl'


def calc_resistance(voltages, currents):
    """
    Fit a linear model to I(V) data and extract electrical parameters.
    Currently assumes a single linear regime over the full dataset.

    Args:
        voltages (array-like): Voltage values.
        currents (array-like): Current values.

    Returns:
        dict: Dictionary containing:
            - resistance_ohm (float): 1/slope of the linear fit
            - intercept (float): fit intercept
            - r_squared (float): coefficient of determination
    """

    # NOTE: full-range fit (simplest baseline)
    # This mixes forward and reverse sweeps and may include nonlinear regions.
    # Future improvements may include:
    #    - separating sweep directions
    #    - restricting to low-bias regions
    #    - piecewise fitting
    slope, intercept, r_value, _, _ = stats.linregress(voltages, currents)

    return {
        'resistance_ohm': 1 / slope,  # assumes I = slope * V
        'intercept': intercept,
        'r_squared': r_value**2,
    }


def compute_elaborations(dataset):
    """
    Compute derived quantities from a single I(V) dataset (raw curve).

    Args:
        dataset (dict): Single measurement containing:
            - metadata
            - curves (Voltage, Current)

    Returns:
        dict: Dictionary of computed elaborations.
    """

    # Convert to numpy for numerical operations
    # (later: could already be stored as arrays or in a dataframe)
    V = np.array(dataset[DATA][KEY_VOLTAGE])
    I = np.array(dataset[DATA][KEY_CURRENT])

    return {
        KEY_GLOBAL_LINEAR_FIT : calc_resistance(V, I),
        # future: add filtering, hysteresis analysis, etc.
    }


def add_elaborations(dataset):
    """
    Return a new dataset enriched with computed elaborations.

    This function does NOT modify the input dataset in place.
    Instead, it returns a new dictionary to preserve immutability
    within the processing pipeline.

    Args:
        dataset (dict): Raw dataset.

    Returns:
        dict: New dataset including an 'elaborations' field.
    """

    # rebuilds dataset and adds a new top-level field
    return {
        **dataset, # dictionary unpacking
        ELABORATIONS : compute_elaborations(dataset)
    }


def dump_data(save_path, data):
    """
    Save processed datasets to a pickle file.

    Args:
        save_path (Path): Output file path.
        data (list of dict): Processed datasets.
    """

    # Pickle is fine for iterative work, but:
    # - not human-readable
    # - not portable across languages
    with open(save_path, 'wb') as f:
        pickle.dump(data, f)

    print(f"Saved {len(data)} curves to {save_path}")


def main():
    """
    Main pipeline:
    - load raw datasets
    - compute elaborations per curve
    - save enriched dataset snapshot
    """

    # Load raw I(V) measurements
    with open(pickle_curves_input, 'rb') as f:
        datasets = pickle.load(f)

    # Curve-level processing (no grouping yet)
    processed_datasets = [add_elaborations(d) for d in datasets]

    # Save intermediate pipeline result
    dump_data(pickle_elaborations_output, processed_datasets)


if __name__ == "__main__":
    main()
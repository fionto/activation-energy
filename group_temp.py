from pathlib import Path
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
pickle_elaborations_input = dataset_dir / 'elaborated_UH70FS.pkl'

# Always write to a new file (avoid accidental overwrite of previous stages)
# This lets me keep intermediate versions while iterating
pickle_temperature_output = dataset_dir / 'temperature_UH70FS.pkl'


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
    - load elaborations
    - group per T
    - starts vdp pipeline
    """

    # Load the dataset containing the elaborations (linear fits)
    with open(pickle_elaborations_input, 'rb') as f:
        datasets = pickle.load(f)

    for dataset in datasets:
        

    # Save intermediate pipeline result
    # dump_data(pickle_temperature_output, grouped_temp_dataset)


if __name__ == "__main__":
    main()
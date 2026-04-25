from pathlib import Path
import pickle

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

    grouped_temp_dataset = {} #placeholder

    # Load the dataset containing the elaborations (linear fits)
    with open(pickle_elaborations_input, 'rb') as f:
        datasets = pickle.load(f)

    #

    # Save intermediate pipeline result
    dump_data(pickle_temperature_output, grouped_temp_dataset)


if __name__ == "__main__":
    main()
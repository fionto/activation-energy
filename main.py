from pathlib import Path
import matplotlib.pyplot as plt
import loaders
import constants
import validators
import utils

def main():
    # CSV DATA MANIPULATION
    # a single .txt file (CSV data) contains one  I(V) measurement
    # the directory contains multiple measurements (.txt files)
    raw_datasets_dir = Path(__file__).parent / 'data' / 'UH70-FS'

    # Validate the entire datasets inside the directory
    directory_content = validators.validate_all_datasets(raw_datasets_dir, constants.FILENAME_PATTERN, verbose=False)
    utils.print_discarded_files_report(directory_content)
    
    # Ingest and transform data to my data structure
    collection = loaders.load_all_datasets(directory_content['accepted'])
    
    # Display and analyze
    print(collection.summary_df)
    
    vdp_results = collection.vdp_df
    print(vdp_results)
    
    vdp_results.plot(x="temp_k", y="sheet_resistance_ohm")
    plt.show()


if __name__ == "__main__":
    main()
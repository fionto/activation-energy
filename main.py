from pathlib import Path
import sys
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

    # VALIDATION PHASE: file-level checks
    try:
        directory_content = validators.validate_all_datasets(
            raw_datasets_dir, constants.FILENAME_PATTERN, verbose=False
        )
    except TypeError as e:
        print(f"❌ Fatal error: Invalid regex pattern\n   {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ Fatal error: No datasets found\n   {e}", file=sys.stderr)
        sys.exit(1)
    except NotADirectoryError as e:
        print(f"❌ Fatal error: Invalid directory path\n   {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"❌ Fatal error: Permission denied accessing directory\n   {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"❌ Fatal error: Filesystem error\n   {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Fatal error: All files were rejected\n   {e}", file=sys.stderr)
        sys.exit(1)

    # Report on rejected files (if any exist)
    utils.print_discarded_files_report(directory_content)
    
    # LOADING PHASE: parse and transform data


    # Load and transform data to my data structure
    collection = loaders.load_all_datasets(directory_content['accepted'])
    
    # Display and analyze
    print(collection.summary_df)
    
    vdp_results = collection.vdp_df
    print(vdp_results)
    
    vdp_results.plot(x="temp_k", y="sheet_resistance_ohm")
    plt.show()


if __name__ == "__main__":
    main()
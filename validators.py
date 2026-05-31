import re
import utils
from pathlib import Path


def validate_filename(filename: str, pattern: re.Pattern) -> bool:
    """Validates if a filename matches a specific naming convention.

    This function checks the provided filename against a pre-defined regular
    expression pattern to ensure it follows the required structural format,
    including specific date-time stamps, sample identifiers, and optional
    sequence suffixes.

    Args:
        filename: The string filename to validate.
        pattern: A compiled regular expression object (typically imported
            from constants.py) defining the naming convention.

    Returns:
        True if the filename perfectly matches the pattern, False otherwise.

    Raises:
        TypeError: If the provided pattern is not a compiled regular
            expression object.

    Examples:
        >>> import re
        >>> from constants import FILENAME_PATTERN
        >>> validate_filename("20260530_143000_SAMPLE_P101bar_T25C_AB.txt", FILENAME_PATTERN)
        True
        >>> validate_filename("invalid_name.txt", FILENAME_PATTERN)
        False
    """

    m = pattern.match(filename)

    return False if not m else True


def validate_dataset_directory(directory_path: Path, verbose: bool = False) -> Path:
    """Validate dataset directory for existence, accessibility, and content.
    
    Args:
        directory_path: Path object pointing to the dataset directory.
        verbose: Whether to print validation messages (default: False).
    
    Returns:
        The validated Path object.
    
    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path exists but is not a directory.
        PermissionError: If the directory cannot be read.
        OSError: For other filesystem-level errors.
    """
    
    # EXISTENCE CHECK
    if not directory_path.exists():
        raise FileNotFoundError(
            f"Directory not found at {directory_path}"
        )

    # TYPE CHECK
    if not directory_path.is_dir():
        raise NotADirectoryError(
            f"Path exists but is not a directory: {directory_path}"
        )
    
    # PERMISSIONS CHECK
    try:
        list(directory_path.iterdir())
    except PermissionError:
        raise PermissionError(
            f"Permission denied reading directory: {directory_path}"
        ) from None
    except OSError as e:
        raise OSError(
            f"OS-level error accessing directory: {directory_path}: {e}"
        ) from e
    
    # SUCCESS
    if verbose:
        print(f"✅ Dataset directory validated successfully at {directory_path.resolve()}")
    
    return directory_path.resolve()


def validate_all_datasets(data_dir: Path, pattern: re.Pattern, verbose: bool = True) -> dict:
    """
    Scans a directory and filters files.
    Crashes hard via SystemExit if no files survive the validation checks.
    Returns a standard dict: {"accepted": [...], "rejected": {...}}
    """
    results = {
        "accepted": [],
        "rejected": {}
    }
    
    validated_dir = validate_dataset_directory(data_dir, verbose=verbose)

    # Grab ALL files in the directory
    all_files = sorted(f for f in validated_dir.iterdir() if f.is_file())

    # CRASH HARD 1: The directory is completely empty of any files
    if not all_files:
        raise ValueError(
            f"\nNo files found in directory: '{validated_dir}'"
        )
    
    for i, measurement_file in enumerate(all_files, 1):
        full_path = measurement_file.resolve()
        
        if verbose:
            print(f"Processing {i}/{len(all_files)}: {measurement_file.name}")
        
        # Check extension
        if measurement_file.suffix.lower() not in {".txt", ".csv"}:
            results["rejected"][full_path] = f"Unsupported file extension ({measurement_file.suffix})"
            continue

        # Check filename pattern
        if not validate_filename(measurement_file.name, pattern):
            results["rejected"][full_path] = "Invalid Filename"
            continue

        # Check file size
        if measurement_file.stat().st_size == 0:
            results["rejected"][full_path] = "Empty file"
            continue

        # Check content readability
        try:
            with open(measurement_file, 'r', encoding='utf-8') as f:
                header = f.readline()
                second_line = f.readline()
                if not second_line:
                    results["rejected"][full_path] = "Empty file after the header"
                    continue
        except PermissionError:
            results["rejected"][full_path] = "Permission Error"
            continue
        except UnicodeDecodeError:
            results["rejected"][full_path] = "UnicodeDecodeError"
            continue
        except OSError as e:
            results["rejected"][full_path] = f"OSError: {e}"
            continue
        
        # File is valid
        results["accepted"].append(full_path)

    # CRASH HARD 2: Files were found, but 100% of them were rejected
    if not results["accepted"]:
        utils.print_discarded_files_report(results)
        raise ValueError(
            f"All {len(results['rejected'])} file(s) in '{validated_dir}' were rejected. "
            f"No valid datasets found."
        )
    
    return results
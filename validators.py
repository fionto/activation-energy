"""Dataset validation module for processing and filtering measurement files.
 
This module provides functions to validate dataset directories and filter files
based on naming conventions, file extensions, and content structure. All validation
errors are raised as exceptions, allowing the caller to handle failures contextually.
 
Typical usage:
    >>> from pathlib import Path
    >>> import re
    >>> from constants import FILENAME_PATTERN
    >>> data_dir = Path("./data")
    >>> results = validate_all_datasets(data_dir, FILENAME_PATTERN, verbose=True)
"""
 
import re
import constants
from pathlib import Path
 
 
def validate_filename(filename: str, pattern: re.Pattern) -> bool:
    """Check if a filename matches the required naming convention pattern.
 
    Validates a filename against a pre-defined regular expression pattern to ensure
    it follows the required structural format (e.g., date-time stamps, sample IDs,
    sequence suffixes).
 
    Args:
        filename: The string filename to validate (e.g., "20260530_143000_SAMPLE_P1e-2mbar_T25C_AB.txt").
        pattern: A compiled regular expression object defining the naming convention
            (typically imported from constants.py).
 
    Returns:
        True if the filename matches the pattern exactly, False otherwise.
 
    Raises:
        TypeError: If pattern is not a compiled regular expression object.
 
    Examples:
        >>> import re
        >>> from constants import FILENAME_PATTERN
        >>> validate_filename("20260530_143000_SAMPLE_P101bar_T25C_AB.txt", FILENAME_PATTERN)
        True
        >>> validate_filename("invalid_name.txt", FILENAME_PATTERN)
        False
    """
    if not isinstance(pattern, re.Pattern):
        raise TypeError(f"pattern must be a compiled regex, got {type(pattern)}")
    
    m = pattern.match(filename)
    return bool(m)


def validate_dataset_directory(directory_path: Path, verbose: bool = False) -> Path:
    """Validate that a directory exists, is accessible, and is readable.
 
    Performs a series of checks on the dataset directory:
    1. Existence check: directory must exist on the filesystem.
    2. Type check: path must point to a directory, not a file.
    3. Permission check: directory must be readable by the current process.
 
    Args:
        directory_path: Path object pointing to the dataset directory.
        verbose: If True, print success message. Defaults to False.
 
    Returns:
        The validated Path object (absolute path).
 
    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path exists but is not a directory.
        PermissionError: If the directory cannot be read due to insufficient permissions.
        OSError: For other filesystem-level errors (e.g., network paths, I/O issues).
 
    Examples:
        >>> from pathlib import Path
        >>> raw_dir = Path("./data/measurements")
        >>> validated_dir = validate_dataset_directory(raw_dir, verbose=True)
        >>> # Proceed safely with file operations
    """
    # Check if directory exists
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found at {directory_path}")
 
    # Check if path is actually a directory (not a file)
    if not directory_path.is_dir():
        raise NotADirectoryError(
            f"Path exists but is not a directory: {directory_path}"
        )
 
    # Check read permissions by attempting to list contents
    try:
        list(directory_path.iterdir())
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied reading directory: {directory_path}"
        ) from None
    except OSError as e:
        raise OSError(
            f"OS-level error accessing directory {directory_path}: {e}"
        ) from e
 
    # All validations passed
    if verbose:
        print(
            f"✅ Dataset directory validated successfully at "
            f"{directory_path.resolve()}"
        )
 
    return directory_path.resolve()



def validate_all_datasets(data_dir: Path, pattern: re.Pattern, verbose: bool = True) -> dict:
    """Scan a directory and validate all dataset files against criteria.
 
    Processes all files in the validated directory and filters them based on:
    1. File extension (.txt or .csv only).
    2. Filename format (must match the naming convention pattern).
    3. File size (must not be empty).
    4. Content readability (must be valid UTF-8 with at least a header and data line).
 
    Files that fail any check are placed in the "rejected" dict with the reason.
    Files that pass all checks are placed in the "accepted" list.
 
    Args:
        data_dir: Path object pointing to the dataset directory to scan.
        pattern: A compiled regular expression object for filename validation.
        verbose: If True, print progress for each file. Defaults to True.
 
    Returns:
        A dict with two keys:
            - "accepted": list of Path objects for valid files.
            - "rejected": dict mapping Path objects to rejection reasons (str).
 
    Raises:
        FileNotFoundError: If the directory does not exist or contains no files.
        NotADirectoryError: If data_dir is not a directory.
        PermissionError: If the directory cannot be read.
        OSError: For other filesystem errors during directory scanning.
        ValueError: If all files in the directory are rejected.
 
    Examples:
        >>> from pathlib import Path
        >>> import re
        >>> from constants import FILENAME_PATTERN
        >>> data_dir = Path("./data/measurements")
        >>> results = validate_all_datasets(data_dir, FILENAME_PATTERN, verbose=True)
        >>> print(f"Valid files: {len(results['accepted'])}")
        >>> print(f"Invalid files: {len(results['rejected'])}")
    """
    results = {"accepted": [], "rejected": {}}
 
    # Validate the directory itself
    validated_dir = validate_dataset_directory(data_dir, verbose=verbose)
 
    # Collect all files in the directory
    all_files = sorted(f for f in validated_dir.iterdir() if f.is_file())
 
    # Require at least one file to be present
    if not all_files:
        raise FileNotFoundError(
            f"No files found in directory: {validated_dir}"
        )
 
    # Process each file
    for i, measurement_file in enumerate(all_files, 1):
        full_path = measurement_file.resolve()
 
        if verbose:
            print(f"Processing {i}/{len(all_files)}: {measurement_file.name}")
 
        # Validate file extension
        if measurement_file.suffix.lower() not in constants.ACCEPTED_EXTENSIONS:
            results["rejected"][full_path] = (
                f"Unsupported file extension: {measurement_file.suffix}"
            )
            continue
 
        # Validate filename against pattern
        # Pass .stem (filename without extension) to decouple the regex pattern 
        # from the file format, keeping pattern matching clean and uniform.
        if not validate_filename(measurement_file.stem, pattern):
            results["rejected"][full_path] = "Filename does not match pattern"
            continue
 
        # Check that file is not empty
        if measurement_file.stat().st_size == 0:
            results["rejected"][full_path] = "Empty file"
            continue
 
        # Validate content: must be readable UTF-8 with at least header + data
        try:
            with open(measurement_file, "r", encoding="utf-8") as f:
                header = f.readline()
                data_line = f.readline()
                if not data_line:
                    results["rejected"][full_path] = (
                        "File contains only header, no data lines"
                    )
                    continue
        except PermissionError:
            results["rejected"][full_path] = "Permission denied reading file"
            continue
        except UnicodeDecodeError:
            results["rejected"][full_path] = "File is not valid UTF-8 encoded"
            continue
        except OSError as e:
            results["rejected"][full_path] = f"Filesystem error: {e}"
            continue
 
        # File passed all validations
        results["accepted"].append(full_path)
 
    # Require at least some files to be accepted
    if not results["accepted"]:
        raise ValueError(
            f"All {len(results['rejected'])} files in {validated_dir} were rejected. "
            f"No valid datasets found."
        )
 
    return results
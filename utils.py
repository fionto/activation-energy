from pathlib import Path

def _safe_float(value_str: str) -> float:
    """
    Converts a string representation of a number to a float.
    Returns float('nan') if conversion fails, to allow error propagation.
    """
    try:
        return float(value_str.strip())
    except ValueError:
        return float("nan")
    

def check_alignment(alignment_str: str | None) -> str | None:
    """
    Validates and normalizes Van der Pauw alignment configuration.

    Args:
        alignment_str: Raw alignment string from filename ('AB', 'BA', or None)

    Returns:
        Normalized alignment string ('horizontal', 'vertical', or None)

    Raises:
        ValueError: if alignment_str is not 'AB', 'BA', or None
    """
    if alignment_str is None:
        return None
    match alignment_str:
        case 'AB':
            return "horizontal"
        case 'BA':
            return "vertical"
        case _:
            raise ValueError(f"Invalid VdP configuration: {alignment_str}")
        

def print_discarded_files_report(validation_results: dict) -> None:
    """
    Prints a formatted summary report of all files that were rejected
    during the dataset validation process.
    """
    rejected_files = validation_results.get("rejected", {})
    accepted_count = len(validation_results.get("accepted", []))
    rejected_count = len(rejected_files)
    total_count = accepted_count + rejected_count

    print("\n" + "=" * 60)
    print("         DATASET VALIDATION DISCARD REPORT         ")
    print("=" * 60)
    print(f"Total Files Scanned: {total_count}")
    print(f"Accepted:            {accepted_count}")
    print(f"Discarded:           {rejected_count}")
    print("-" * 60)

    if not rejected_files:
        print("✅ Clean run! No files were discarded.")
        print("=" * 60 + "\n")
        return

    print(f"{'FILE NAME':<35} | {'REASON FOR DISCARD'}")
    print("-" * 60)

    # Sort by path name so the output is deterministic and organized
    for file_path, reason in sorted(rejected_files.items(), key=lambda x: x[0].name):
        # If the key is a string instead of a Path object, convert it
        path_obj = Path(file_path) if isinstance(file_path, str) else file_path
        
        # Print the concise table row
        print(f"{path_obj.name:<35} | {reason}")
        # Print the full path indented underneath for debugging context
        print(f"  └─ Source: {path_obj}")
        print()

    print("=" * 60 + "\n")
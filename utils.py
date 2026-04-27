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
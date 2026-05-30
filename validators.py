import re

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

    
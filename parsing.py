row_str = '1.00000E+1, 4.81472E-9, 1.79020E-10, 0.00000E+0, 1.00000E+1, 0.00000E+0, 0.00000E+0'

def _safe_float(value_str: str) -> float:
    """
    Converts a string representation of a number to a float.

    This function handles whitespace stripping and catches conversion errors 
    gracefully to prevent pipeline crashes on dirty data.

    Args:
        value_str (str): The string value to convert (e.g., " 18.9 ", "").

    Returns:
        float: The converted floating-point number. If conversion fails 
            (e.g., empty string or non-numeric text), returns float('nan').
    """
    try:
        return float(value_str.strip())
    except ValueError:
        # I chose 'nan' instead of 0.0 because 'nan' propagates through math operations.
        return float("nan")

# In questa funzione voglio mantenere solamente Voltage, Current, Standard Deviation
def parse_row(row_str: str) -> dict | None:
    
    if not row_str or not row_str.strip():
        return None
    
    fields = [f.strip() for f in row_str.split(',')]

    voltage_str, current_str, std_dev_str = fields[:3]

    return {
        'voltage' : _safe_float(voltage_str),
        'current' : _safe_float(current_str),
        'std_dev' : _safe_float(std_dev_str),
    }

results = parse_row(row_str)

print(results)
from typing import Any


def join_values(values: set[Any], /) -> str:
    """
    Concatenate values into a formatted string.

    Parameters
    ----------
    values : set[str]; positional-only
        Values.

    Returns
    -------
    values : str
        Comma-delimited string of the values.
    """
    return ", ".join(repr(value) for value in sorted(values))

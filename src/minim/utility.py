"""
Utility functions
=================
.. moduleauthor:: Benjamin Ye <GitHub: @bbye98>

This module contains a collection of utility functions.
"""

from typing import Any, Sequence, Union

try:
    import Levenshtein
    FOUND_LEVENSHTEIN = True
except:
    FOUND_LEVELSHTEIN = False
try:
    import numpy as np
    FOUND_NUMPY = True
except:
    FOUND_NUMPY = False

def levenshtein_ratio(base: str, values: Union[str, Sequence[str]]) -> float:

    """
    Compute the Levenshtein ratio, a measure of similarity, for
    string(s) with respect to a reference string.

    Parameters
    ----------
    base : `str`
        Reference string.

    values : `str` or `Sequence`
        String(s) to compare with `base`.

    Returns
    -------
    ratios : `float` or `numpy.ndarray`
        Levenshtein ratio(s).
    """
    if not FOUND_LEVENSHTEIN or not FOUND_NUMPY:
        emsg = ("Either the Levenshtein or the NumPy library was not "
                "found.")
        raise ImportError(emsg)
    
    if isinstance(values, str):
        return Levenshtein.ratio(base, values)
    return np.fromiter((Levenshtein.ratio(base, v) for v in values),
                       dtype=float, count=len(values))

def multivalue_formatter(
        value: Any, multivalue: bool, *, primary: bool = False,
        sep: Union[str, Sequence[str]] = (", ", " & ")) -> Any:
    
    """
    Format a field value based on whether multivalue for that field is 
    supported.

    Parameters
    ----------
    value : `Any`
        Field value to format.

    multivalue : `bool`
        Determines whether multivalue tags are supported (:code:`True`)
        or should be concatenated (:code:`False`) using the separator(s)
        specified in `sep`.

    primary : `bool`, keyword-only, default: :code:`False`
        Specifies whether the first item in `value` should be used when
        `value` is a `Sequence` and :code:`multivalue=False`.

    sep : `str` or `tuple`, keyword-only, default: :code:`(", ", " & ")`
        Separator(s) to use to concatenate multivalue tags. If a 
        :code:`str` is provided, it is used to concatenate all values.
        If a :code:`tuple` is provided, the first :code:`str` is used to
        concatenate the first :math:`n - 1` values, and the second
        :code:`str` is used to append the final value. 
    """

    if isinstance(value, list):
        if not multivalue:
            if len(value) == 1 or primary:
                return value[0]
            elif isinstance(value[0], str):
                if isinstance(sep, str):
                    return sep.join(value)
                return f"{sep[0].join(value[:-1])}{sep[1]}{value[-1]}"
    elif multivalue:
        return [value]
    return value

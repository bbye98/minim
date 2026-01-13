from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import DeezerResourceAPI
from .users import UsersAPI


class TracksAPI(DeezerResourceAPI):
    """
    Tracks API endpoints for the Deezer API.

    .. note::

       This class is managed by :class:`minim.api.deezer.DeezerAPI` and
       should not be instantiated directly.
    """

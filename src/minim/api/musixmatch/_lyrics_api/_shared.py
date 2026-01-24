from typing import TYPE_CHECKING

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import MusixmatchLyricsAPI


class MusixmatchResourceAPI(ResourceAPI):
    """
    Base class for Musixmatch Lyrics API resource endpoint groups.
    """

    _client: "MusixmatchLyricsAPI"

    @staticmethod
    def _validate_sort_order(
        sort_order: str, /, *, sort_by: str | None = None
    ) -> None:
        """
        Validate sort order.

        Parameters
        ----------
        sort_order : str; positional-only
            Sort order.
        """
        allowed_sort_orders = {"asc", "desc"}
        if sort_order.lower() not in allowed_sort_orders:
            raise ValueError(
                f"Invalid {'' if sort_by is None else sort_by + ' '}"
                f"sort order: {sort_order!r}. Valid values: "
                f"{', '.join(allowed_sort_orders)}."
            )

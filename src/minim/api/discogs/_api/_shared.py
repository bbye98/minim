from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import DiscogsAPIClient


class DiscogsResourceAPI(ResourceAPI):
    """
    Base class for Discogs API resource endpoint groups.
    """

    _RELATIONSHIPS: set[str]
    _client: "DiscogsAPIClient"

    _CURRENCIES = {
        "USD",
        "GBP",
        "EUR",
        "CAD",
        "AUD",
        "JPY",
        "CHF",
        "MXN",
        "BRL",
        "NZD",
        "SEK",
        "ZAR",
    }

    def _resolve_username(self, username: str | None = None, /) -> str:
        """
        Resolve or validate a username for a Discogs API request.

        Parameters
        ----------
        username : str; positional-only; optional
            Username. If not provided, the username of the current user
            is used. Only optional when authenticated.

        Return
        ------
        username : str
            Username.
        """
        if username is None:
            try:
                return self._client._identity["username"]
            except RuntimeError:
                raise RuntimeError(
                    "`username` must be provided when unauthenticated."
                ) from None
        else:
            return self._prepare_string("username", username)

    def _get_paginated_resources(
        self,
        endpoint: str,
        /,
        *,
        limit: int | None = None,
        page: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get paginated Discogs catalog information for one or more items
        of a resource type.

        Parameters
        ----------
        endpoint : str; positional-only
            API endpoint.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        params : dict[str, Any]; keyword-only; optional
            Query parameters to include in the request. If not provided,
            an empty dictionary will be created.

            .. note::

               This `dict` is mutated in-place.

        Returns
        -------
        items : dict[str, Any]
            Page of Qobuz content metadata for the items in the
            resource.
        """
        if params is None:
            params = {}
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if page is not None:
            self._validate_number("page", page, int, 0)
            params["page"] = page
        return self._client._request("GET", endpoint, params=params).json()

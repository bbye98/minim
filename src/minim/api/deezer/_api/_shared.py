from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import DeezerAPI


class DeezerResourceAPI(ResourceAPI):
    """
    Base class for Deezer API resource endpoint groups.
    """

    _client: "DeezerAPI"

    @staticmethod
    def _prepare_deezer_ids(
        deezer_ids: int | str | list[int | str], /
    ) -> tuple[str, int]:
        """
        Normalize, validate, and serialize Deezer IDs.

        Parameters
        ----------
        deezer_ids : int, str, or list[int | str]; positional-only
            Deezer IDs.

        Returns
        -------
        deezer_ids : str
            Comma-separated string of Deezer IDs.

        num_ids : int
            Number of Deezer IDs.
        """
        if isinstance(deezer_ids, int):
            return str(deezer_ids), 1
        if isinstance(deezer_ids, str):
            return DeezerResourceAPI._prepare_deezer_ids(deezer_ids.split(","))
        DeezerResourceAPI._validate_deezer_ids(deezer_ids)
        return ",".join(str(deezer_id) for deezer_id in deezer_ids), len(
            deezer_ids
        )

    @staticmethod
    def _validate_deezer_ids(
        deezer_ids: int | str | list[int | str], /, *, _recursive: bool = True
    ) -> None:
        """
        Validate one or more Deezer IDs.

        Parameters
        ----------
        deezer_ids : int, str, or list[int | str]; positional-only
            Deezer IDs.
        """
        if not isinstance(deezer_ids, int) and not deezer_ids:
            raise ValueError("At least one Deezer ID must be specified.")

        if isinstance(deezer_ids, str):
            if _recursive:
                DeezerResourceAPI._validate_deezer_ids(deezer_ids.split(","))
            elif not (
                deezer_ids.lstrip("-").isdecimal() or deezer_ids == "me"
            ):
                raise ValueError(f"Invalid Deezer ID {deezer_ids!r}.")
        elif not isinstance(deezer_ids, int):
            if _recursive:
                if not isinstance(deezer_ids, tuple | list | str):
                    raise TypeError(
                        "Deezer IDs must be provided as integers, "
                        "strings, or lists of integers and/or strings."
                    )
                for deezer_id in deezer_ids:
                    DeezerResourceAPI._validate_deezer_ids(
                        deezer_id, _recursive=False
                    )
            else:
                raise ValueError(f"Invalid Deezer ID {deezer_ids!r}.")

    def _request_resource_relationship(
        self,
        method: str,
        resource_type: str,
        resource_id: int | str,
        relationship: str | None = None,
        /,
        *,
        limit: int | None = None,
        offset: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get Deezer catalog information for a resource related to an
        item.

        Parameters
        ----------
        method : str
            HTTP method.

        resource_type : str; positional-only
            Resource type.

        resource_id : str; positional-only
            Deezer ID of the resource.

        relationship : str; positional-only
            Related resource type.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Minimum value**: :code:`1`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next batch of items.

            **Minimum value**: :code:`0`.

        params : dict[str, Any]; keyword-only; optional
            Dictionary of additional query parameters to include in the
            request. If not provided, a new dictionary will be created.

            .. note::

               This `dict` is mutated in-place.

        Returns
        -------
        resource : dict[str, Any]
            Deezer content metadata for the related resource.
        """
        self._validate_deezer_ids(resource_id, _recursive=False)
        if params is None:
            params = {}
        if limit is not None:
            self._validate_number("limit", limit, int, 1)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["index"] = offset
        endpoint = f"{resource_type}/{resource_id}"
        if relationship is not None:
            endpoint += f"/{relationship}"
        return self._client._request(method, endpoint, params=params).json()

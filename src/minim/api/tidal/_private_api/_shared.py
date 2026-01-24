from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI
from .._api._shared import TIDALResourceAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPIClient


class PrivateTIDALResourceAPI(ResourceAPI):
    """
    Base class for private TIDAL API resource endpoint groups.
    """

    _PLAYBACK_MODES = {"STREAM", "OFFLINE"}
    _client: "PrivateTIDALAPIClient"

    _validate_tidal_ids = TIDALResourceAPI._validate_tidal_ids

    @staticmethod
    def _prepare_tidal_ids(
        tidal_ids: str | list[str], /, *, limit: int = 500
    ) -> str:
        """
        Normalize, validate, and serialize TIDAL IDs.

        Parameters
        ----------
        tidal_ids : int, str, or list[str]; positional-only
            Comma-separated string or list of TIDAL IDs.

        limit : int; keyword-only, default: :code:`500`
            Maximum number of TIDAL IDs that can be sent in the
            request.

        Returns
        -------
        tidal_ids : str
            Comma-separated string of TIDAL IDs.
        """
        if not tidal_ids:
            raise ValueError("At least one TIDAL ID must be specified.")

        if isinstance(tidal_ids, int):
            return str(tidal_ids)

        if isinstance(tidal_ids, str):
            return PrivateTIDALResourceAPI._prepare_tidal_ids(
                tidal_ids.split(","), limit=limit
            )

        num_ids = len(tidal_ids)
        if num_ids > limit:
            raise ValueError(
                f"A maximum of {limit} TIDAL IDs can be sent in a request."
            )
        for idx, id_ in enumerate(tidal_ids):
            if isinstance(id_, int):
                tidal_ids[idx] = str(id_)
            elif isinstance(id_, str):
                tidal_ids[idx] = id_ = id_.strip()
                if not id_.isdecimal():
                    raise ValueError(f"Invalid TIDAL ID {id_!r}.")
            else:
                raise ValueError(f"Invalid TIDAL ID {id_!r}.")
        return ",".join(tidal_ids)

    @staticmethod
    def _prepare_uuids(
        resource_type: str,
        resource_uuids: str | list[str],
        /,
        *,
        has_prefix: bool = False,
    ) -> str:
        """
        Normalize, validate, and serialize UUIDs.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

            **Valid values**: :code:`"folder"`, :code:`"playlist"`.

        resource_uuids : str or list[str]; positional-only
            UUIDs of playlists or playlist folders.

        has_prefix : bool; keyword-only; default: :code:`False`
            Whether UUIDs are prefixed with :code:`trn:{type}:`.

        Returns
        -------
        resource_uuids : str
            Comma-separated string containing UUIDs of playlists or
            playlist folders.
        """
        if not resource_uuids:
            raise ValueError(
                f"At least one {resource_type} UUID must be specified."
            )

        if isinstance(resource_uuids, str):
            return PrivateTIDALResourceAPI._prepare_uuids(
                resource_uuids.split(",")
            )
        elif isinstance(resource_uuids, tuple | list):
            for idx, uuid in enumerate(resource_uuids):
                if has_prefix:
                    if uuid.startswith(f"trn:{resource_type}:"):
                        uuid = uuid[13:]
                    else:
                        resource_uuids[idx] = f"trn:{resource_type}:{uuid}"
                ResourceAPI._validate_uuid(uuid)
        else:
            raise TypeError(
                f"`{resource_type}_uuids` must be a comma-separated "
                "string or a list of strings."
            )

        return ",".join(resource_uuids)

    def _get_resource(
        self,
        resource_type: str,
        resource_id: str,
        /,
        country_code: str | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a resource.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

        resource_id : str; positional-only
            TIDAL ID of the resource.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL content metadata for the resource.
        """
        if country_code is None:
            country_code = self._client._my_country_code
        else:
            self._validate_country_code(country_code)
        return self._client._request(
            "GET",
            f"v1/{resource_type}/{resource_id}",
            params={"countryCode": country_code},
        ).json()

    def _get_resource_relationship(
        self,
        resource_type: str,
        resource_id: int | str,
        relationship: str,
        /,
        country_code: str | None = None,
        *,
        limit: int | None = None,
        offset: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a resource related to an item.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

        resource_id : str; positional-only
            TIDAL ID of the resource.

        relationship : str; positional-only
            Related resource type.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the current user account or IP
            address is used.

        limit : int; keyword-only; optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`10`.

        offset : int; keyword-only; optional
            Index of the first item to return. Use with `limit` to get
            the next batch of items.

            **Minimum value**: :code:`0`.

            **API default**: :code:`0`.

        params : dict[str, Any]; keyword-only; optional
            Dictionary of additional query parameters to include in the
            request. If not provided, a new dictionary will be created.

            .. note::

               This `dict` is mutated in-place.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL content metadata for the related resource.
        """
        if params is None:
            params = {}
        self._client._resolve_country_code(country_code, params)
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 100)
            params["limit"] = limit
        if offset is not None:
            self._validate_number("offset", offset, int, 0)
            params["offset"] = offset
        return self._client._request(
            "GET",
            f"v1/{resource_type}/{resource_id}/{relationship}",
            params=params,
        ).json()

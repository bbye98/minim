from __future__ import annotations
from typing import TYPE_CHECKING

from ...._types import COLLECTION_TYPES, ORDERED_COLLECTION_TYPES
from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from typing import Any

    from ...._types import Collection
    from .. import TIDALAPIClient


class TIDALResourceAPI(ResourceAPI):
    """
    Base class for TIDAL API resource endpoint groups.
    """

    _RELATIONSHIPS: set[str]
    _client: "TIDALAPIClient"

    @staticmethod
    def _process_sort(
        sort_by: str,
        /,
        *,
        descending: bool | None,
        prefix: str,
        sort_fields: set[str],
        params: dict[str, Any],
    ) -> None:
        """
        Process sort.

        Parameters
        ----------
        sort_by : str; positional-only
            Field to sort the returned items by.

        descending : bool; keyword-only
            Whether to sort in descending order.

        prefix : str; keyword-only
            Sort field prefix.

        sort_fields : set[str]; keyword-only
            Valid fields to sort by.

        params : dict[str, Any]; keyword-only
            Query parameters to include in the request. If not provided,
            an empty dictionary will be created.

            .. note::

               This `dict` is mutated in-place.
        """
        ResourceAPI._validate_type("sort_by", sort_by, str)
        sort_by = sort_by.removeprefix(prefix)
        if sort_by not in sort_fields:
            raise ValueError(
                f"Cannot sort by '{prefix}{sort_by}'. Valid values: "
                f"{ResourceAPI._join_values([f'{prefix}{sort_field}' for sort_field in sort_fields])}."
            )
        params["sort"] = f"{'-' if descending else ''}{prefix}{sort_by}"

    @staticmethod
    def _validate_tidal_ids(
        tidal_ids: int | str | Collection[int | str],
        /,
        *,
        recursive: bool = True,
    ) -> None:
        """
        Validate one or more TIDAL IDs.

        Parameters
        ----------
        tidal_ids : int, str, or Collection[int | str]; positional-only
            TIDAL IDs.
        """
        if not isinstance(tidal_ids, int) and not tidal_ids:
            raise ValueError("At least one TIDAL ID must be specified.")

        if isinstance(tidal_ids, str):
            if not tidal_ids == "me" and not tidal_ids.isdecimal():
                raise ValueError(f"Invalid TIDAL ID {tidal_ids!r}.")

        elif not isinstance(tidal_ids, int):
            if recursive:
                if not isinstance(tidal_ids, str | COLLECTION_TYPES):
                    raise ValueError("TIDAL IDs must be integers or strings.")

                for tidal_id in tidal_ids:
                    TIDALResourceAPI._validate_tidal_ids(
                        tidal_id, recursive=False
                    )
            else:
                raise ValueError(f"Invalid TIDAL ID {tidal_ids!r}.")

    @classmethod
    def _prepare_expand(
        cls,
        expand: str | Collection[str],
        /,
        *,
        relationships: set[str] | None = None,
    ) -> list[str]:
        """
        Validate, normalize, and prepare a collection of related
        resources.

        Parameters
        ----------
        expand : str | Collection[str]; positional-only
            Related resources to include metadata for in the response.

        resources : set[str]; keyword-only; optional
            Valid related resources. If not specified,
            :code:`cls._RELATIONSHIPS` is used.

        Returns
        -------
        expand : list[str]
            List of related resources to include metadata for.
        """
        if relationships is None:
            relationships = getattr(cls, "_RELATIONSHIPS", {})
        if isinstance(expand, str):
            expand = [expand]
        elif not isinstance(expand, COLLECTION_TYPES):
            raise ValueError(
                "`expand` must be a string or a collection of strings."
            )
        for resource in expand:
            if resource not in relationships:
                raise ValueError(
                    f"Invalid related resource {resource!r}. Valid "
                    f"values: {ResourceAPI._join_values(relationships)}."
                )
        return (
            expand
            if isinstance(expand, ORDERED_COLLECTION_TYPES)
            else sorted(expand)
        )

    def _get_resources(
        self,
        resource_type: str,
        resource_identifiers: str | Collection[str] | None,
        /,
        country_code: str | None = None,
        *,
        locale: str | None = None,
        include_explicit: bool | None = None,
        expand: str | Collection[str] | None = None,
        cursor: str | None = None,
        share_code: str | None = None,
        relationships: set[str] | None = None,
        resource_identifier_type: str = "id",
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for one or more items of a
        resource type.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

        resource_identifiers : str or Collection[str]; positional-only
            TIDAL IDs or UUIDs of the resources, or a search query.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        include_explicit : bool; keyword-only; optional
            Whether to include explicit content in the results.

            **API default**: :code:`True`.

        expand : str or Collection[str]; keyword-only; optional
            Related resources to include metadata for in the response.

        cursor : str; keyword-only; optional
            Cursor for for fetching the next page of results when
            retrieving multiple albums.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        relationships : set[str]; keyword-only; optional
            Allowed related resource types. If not provided, the
            :code:`_RELATIONSHIPS` attribute is used.

        resource_identifier_type : str; keyword-only; \
        default: :code:`"id"`
            Resource identifier type.

            **Valid values**: :code:`"id"`, :code:`"uuid"`,
            :code:`"query"`.

        params : dict[str, Any]; keyword-only; optional
            Query parameters to include in the request. If not provided,
            an empty dictionary will be created.

            .. note::

               This `dict` is mutated in-place.

        Returns
        -------
        resources : dict[str, Any]
            TIDAL metadata for the resources.
        """
        if params is None:
            params = {}
        if country_code is not None:
            self._validate_country_code(country_code)
            params["countryCode"] = country_code
        if locale is not None:
            self._validate_locale(locale)
            params["locale"] = locale
        if include_explicit is not None:
            self._validate_type("include_explicit", include_explicit, bool)
            params["explicitFilter"] = (
                "INCLUDE" if include_explicit else "EXCLUDE"
            )
        if expand is not None:
            params["include"] = self._prepare_expand(
                expand, relationships=relationships or self._RELATIONSHIPS
            )
        if resource_identifiers is not None:
            if resource_identifier_type == "id":
                self._validate_tidal_ids(resource_identifiers)
            elif resource_identifier_type == "uuid":
                self._validate_uuids(resource_identifiers)
            else:
                self._validate_type("query", resource_identifiers, str)
            if isinstance(resource_identifiers, int | str):
                return self._client._request(
                    "GET",
                    f"{resource_type}/{resource_identifiers}",
                    params=params,
                ).json()

            params["filter[id]"] = (
                resource_identifiers
                if isinstance(resource_identifiers, ORDERED_COLLECTION_TYPES)
                else sorted(resource_identifiers)
            )
        if cursor is not None:
            params["page[cursor]"] = self._prepare_string("cursor", cursor)
        if share_code is not None:
            params["shareCode"] = self._prepare_string(
                "share_code", share_code
            )
        return self._client._request(
            "GET", resource_type, params=params
        ).json()

    def _get_resource_relationship(
        self,
        resource_type: str,
        resource_identifier: int | str,
        relationship: str,
        /,
        country_code: str | None = None,
        *,
        locale: str | None = None,
        include_explicit: bool | None = None,
        include_metadata: bool = False,
        cursor: str | None = None,
        share_code: str | None = None,
        resource_identifier_type: str = "id",
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for a resource related to an item.

        Parameters
        ----------
        resource_type : str; positional-only
            Resource type.

        resource_identifier : str; positional-only
            TIDAL ID or UUID of the resource, or a search query.

        relationship : str; positional-only
            Related resource type.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag.

        include_explicit : bool; keyword-only; optional
            Whether to include explicit content in the results.

            **API default**: :code:`True`.

        include_metadata : bool; keyword-only; default: :code:`False`
            Whether to include metadata for the related
            resource.

        cursor : str; keyword-only; optional
            Cursor for for fetching the next page of results when
            retrieving multiple albums.

        share_code : str; keyword-only; optional
            Share code that grants access to unlisted resources.

        resource_identifier_type : str; keyword-only; \
        default: :code:`"id"`
            Resource identifier type.

            **Valid values**: :code:`"id"`, :code:`"uuid"`,
            :code:`"query"`.

        params : dict[str, Any]; keyword-only; optional
            Query parameters to include in the request. If not provided,
            an empty dictionary will be created.

            .. note::

               This `dict` is mutated in-place.

        Returns
        -------
        resource : dict[str, Any]
            TIDAL metadata for the related resource.
        """
        if resource_identifier_type == "id":
            self._validate_tidal_ids(resource_identifier, recursive=False)
        elif resource_identifier_type == "uuid":
            self._validate_uuids(resource_identifier)
        else:
            self._validate_type("query", resource_identifier, str)
        if params is None:
            params = {}
        if country_code is not None:
            self._validate_country_code(country_code)
            params["countryCode"] = country_code
        if locale is not None:
            self._validate_locale(locale)
            params["locale"] = locale
        if include_explicit is not None:
            self._validate_type("include_explicit", include_explicit, bool)
            params["explicitFilter"] = (
                "INCLUDE" if include_explicit else "EXCLUDE"
            )
        if include_metadata is not None:
            self._validate_type("include_metadata", include_metadata, bool)
            if include_metadata:
                params["include"] = relationship
        if cursor is not None:
            params["page[cursor]"] = self._prepare_string("cursor", cursor)
        if share_code is not None:
            params["shareCode"] = self._prepare_string(
                "share_code", share_code
            )
        return self._client._request(
            "GET",
            f"{resource_type}/{resource_identifier}/relationships/{relationship}",
            params=params,
        ).json()

from typing import Any

from ..._shared import TTLCache
from ._shared import DiscogsResourceAPI


class MarketplaceAPI(DiscogsResourceAPI):
    """
    Marketplace API endpoints for the Discogs API.

    .. important::

       This class is managed by
       :class:`minim.api.discogs.DiscogsAPIClient` and should not be
       instantiated directly.
    """

    _CONDITIONS = {
        "Mint (M)",
        "Near Mint (NM or M-)",
        "Very Good Plus (VG+)",
        "Very Good (VG)",
        "Good Plus (G+)",
        "Good (G)",
        "Fair (F)",
        "Poor (P)",
    }
    _IMMUTABLE_STATUSES = {
        "All",
        "Deleted",
        "Expired",
        "Sold",
        "Suspended",
        "Violation",
    }
    _MUTABLE_STATUSES = {"Draft", "For Sale"}
    _SORT_FIELDS = {
        "artist",
        "audio",
        "catno",
        "item",
        "label",
        "listed",
        "location",
        "price",
        "status",
    }

    def _upsert_listing(
        self,
        endpoint_suffix: str = "",
        /,
        *,
        allow_offers: bool | None = None,
        media_condition: str | None = None,
        price: float | None = None,
        private_notes: str | None = None,
        public_notes: str | None = None,
        status: str | None = None,
        shipping_count: float | str | None = None,
        storage_location: str | None = None,
        sleeve_condition: str | None = None,
        weight: float | str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Create or update a marketplace listing.

        Parameters
        ----------
        endpoint_suffix : str; positional-only; default: :code:`""`
            Endpoint suffix containing the ID of an existing listing.

        allow_offers : bool; keyword-only; optional
            Whether to accept offers for the listed item.

            **API default**: :code:`False`.

        media_condition : str; keyword-only; optional
            Media condition.

            **Valid values**: :code:`"Mint (M)"`,
            :code:`"Near Mint (NM or M-)"`,
            :code:`"Very Good Plus (VG+)"`, :code:`"Very Good (VG)"`,
            :code:`"Good Plus (G+)"`, :code:`"Good (G)"`,
            :code:`"Fair (F)"`, :code:`"Poor (P)"`.

        price : float; keyword-only; optional
            Listing price.

        private_notes : str; keyword-only; optional
            Private comments (e.g., external IDs) that are visible to
            only the seller.

        public_notes : str; keyword-only; optional
            Public comments (e.g., item condition) that are displayed to
            the buyers.

        status : str; keyword-only; optional
            Listing status.

            **Valid values**: :code:`"Draft"`, :code:`"For Sale"`.

        shipping_count : float or str; keyword-only; optional
            Number of items the listing counts as for the purpose of
            calculating the shipping cost. Use :code:`"auto"` to
            automatically estimate the quantity.

        storage_location : str; keyword-only; optional
            Identifier for the item's physical storage location that is
            visible to only the seller.

        sleeve_condition : str; keyword-only; optional
            Sleeve condition.

            **Valid values**: :code:`"Mint (M)"`,
            :code:`"Near Mint (NM or M-)"`,
            :code:`"Very Good Plus (VG+)"`, :code:`"Very Good (VG)"`,
            :code:`"Good Plus (G+)"`, :code:`"Good (G)"`,
            :code:`"Fair (F)"`, :code:`"Poor (P)"`, :code:`"Generic"`,
            :code:`"Not Graded"`, :code:`"No Cover"`.

        weight : float or str; keyword-only; optional
            Weight of the item in grams for the purpose of calculating
            the shipping cost. Use :code:`"auto"` to automatically
            estimate the value.

        payload : dict[str, Any]; keyword-only; optional
            JSON payload to include in the request.

        Returns
        -------
        listing : dict[str, Any] or None
            Discogs content metadata for a newly created listing or
            :code:`None` for an updated listing.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "listing_id": <int>,
                    "resource_url": <str>
                  }
        """
        if payload is None:
            payload = {}
        if allow_offers is not None:
            self._validate_type("allow_offers", allow_offers, bool)
            payload["allow_offers"] = allow_offers
        if media_condition is not None:
            media_condition = self._prepare_string(
                "media_condition", media_condition
            )
            if media_condition not in self._CONDITIONS:
                raise ValueError(
                    f"Invalid media condition {media_condition!r}. "
                    f"Valid values: {self._join_values(self._CONDITIONS)}."
                )
            payload["condition"] = media_condition
        if price is not None:
            self._validate_number("price", price, int | float, 0.01)
            payload["price"] = round(price, 2)
        if private_notes is not None:
            self._validate_type("private_notes", private_notes, str)
            payload["external_id"] = private_notes
        if public_notes is not None:
            self._validate_type("public_notes", public_notes, str)
            payload["comments"] = public_notes
        if status is not None:
            status = self._prepare_string("status", status).capitalize()
            if status not in self._MUTABLE_STATUSES:
                raise ValueError(
                    f"Invalid status {status!r}. Valid values: "
                    f"{self._join_values(self._MUTABLE_STATUSES)}."
                )
            payload["status"] = status
        if shipping_count is not None:
            if shipping_count != "auto":
                self._validate_number(
                    "shipping_count", shipping_count, int | float, 0
                )
            payload["format_quantity"] = shipping_count
        if storage_location is not None:
            self._validate_type("storage_location", storage_location, str)
            payload["location"] = storage_location
        if sleeve_condition is not None:
            sleeve_condition = self._prepare_string(
                "sleeve_condition", sleeve_condition
            )
            if sleeve_condition not in (
                conditions := self._CONDITIONS
                | {"Generic", "Not Graded", "No Cover"}
            ):
                raise ValueError(
                    f"Invalid sleeve condition {sleeve_condition!r}. "
                    f"Valid values: {self._join_values(conditions)}."
                )
            payload["sleeve_condition"] = sleeve_condition
        if weight is not None:
            if weight != "auto":
                self._validate_number("weight", weight, int | float, 0)
            payload["weight"] = weight
        resp = self._client._request(
            "POST", f"marketplace/listings{endpoint_suffix}", json=payload
        )
        if not endpoint_suffix:
            return resp.json()

    @TTLCache.cached_method(ttl="user")
    def get_user_inventory(
        self,
        username: str | None = None,
        /,
        *,
        status: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        `Marketplace > Inventory <https://www.discogs.com/developers
        /#page:marketplace,header:marketplace-inventory>`_: Get Discogs
        catalog information for a seller's inventory.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access private listings and the :code:`weight`,
                    :code:`format_quantity`, :code:`external_id`,
                    :code:`location`, and :code:`quantity` keys if
                    authenticated as the requested user.

        Parameters
        ----------
        username : str; positional-only; optional
            Username of the user. If not provided, the username of the
            current user is used. Only optional when authenticated.

            **Example**: :code:`"rodneyfool"`.

        status : str; keyword-only; optional
            Listing status to filter by.

            **Valid values**: :code:`"All"`, :code:`"Deleted"`,
            :code:`"Draft"`, :code:`"Expired"`, :code:`"For Sale"`,
            :code:`"Sold"`, :code:`"Suspended"`, :code:`"Violation"`.

        limit : int; keyword-only; optional
            Maximum number of releases to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            releases.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        sort_by : str; keyword-only; optional
            Field to sort the returned items by.

            **Valid values**: :code:`"listed"`, :code:`"price"`,
            :code:`"item"`, :code:`"artist"`, :code:`"label"`,
            :code:`"catno"`, :code:`"audio"`, :code:`"status"`,
            :code:`"location"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

        Returns
        -------
        inventory : dict[str, Any]
            Page of Discogs content metadata for the seller's inventory.

            .. admonition:: Sample responses
               :class: response dropdown

               .. code::

                  {
                    "listings": [
                      {
                        "allow_offers": <bool>,
                        "audio": <bool>,
                        "comments": <str>,
                        "condition": <str>,
                        "id": <int>,
                        "posted": <str>,
                        "price": {
                          "currency": <str>,
                          "value": <float>
                        },
                        "release": {
                          "artist": <str>,
                          "catalog_number": <str>,
                          "description": <str>,
                          "format": <str>,
                          "id": <int>,
                          "resource_url":  <str>,
                          "thumbnail": <str>,
                          "title": <str>,
                          "year": <int>
                        },
                        "resource_url": <str>,
                        "seller": {
                          "id": <int>,
                          "resource_url": <str>,
                          "username": <str>
                        },
                        "ships_from": <str>,
                        "sleeve_condition": <str>,
                        "status": <str>,
                        "uri": <str>
                      }
                    ],
                    "pagination": {
                      "items": <int>,
                      "page": <int>,
                      "pages": <int>,
                      "per_page": <int>,
                      "urls": {
                        "first": <str>,
                        "last": <str>,
                        "next": <str>,
                        "prev": <str>
                      }
                    }
                  }
        """
        params = {}
        if status is not None:
            status = self._prepare_string("status", status).capitalize()
            if status not in (
                statuses := self._IMMUTABLE_STATUSES | self._MUTABLE_STATUSES
            ):
                raise ValueError(
                    f"Invalid status {status!r}. "
                    f"Valid values: {self._join_values(statuses)}."
                )
        if sort_by is not None:
            sort_by = self._prepare_string("sort_by", sort_by).lower()
            if sort_by not in self._SORT_FIELDS:
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid "
                    f"values: {self._join_values(self._SORT_FIELDS)}."
                )

            if sort_by in {"status", "location"}:
                self._client._require_authentication(
                    "marketplace.get_user_inventory"
                )
        if descending is not None:
            self._validate_type("descending", descending, bool)
            params["sort_order"] = "desc" if descending else "asc"
        return self._get_paginated_resources(
            f"users/{self._resolve_username(username)}/inventory",
            limit=limit,
            page=page,
            params=params,
        )

    @TTLCache.cached_method(ttl="user")
    def get_listing(
        self,
        listing_id: int | str,
        /,
        *,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """
        `Marketplace > Listing > Get Listing <https://www.discogs.com
        /developers/#page:marketplace,header:marketplace-listing>`_: Get
        Discogs catalog information for a marketplace listing.

        .. admonition:: User authentication
           :class: entitlement dropdown

           .. tab-set::

              .. tab-item:: Optional

                 User authentication
                    Access the :code:`in_cart` key if authenticated, and
                    the :code:`weight`, :code:`format_quantity`,
                    :code:`external_id`, :code:`location`, and
                    :code:`quantity` keys if authenticated as the
                    listing's owner.

        Parameters
        ----------
        listing_id : int or str; positional-only; optional
            Discogs ID of the listing.

            **Examples**: :code:`172723812`, :code:`"2983532888"`.

        currency : str; keyword-only; optional
            Currency for marketplace data.

            **Valid values**: :code:`"USD"`, :code:`"GBP"`,
            :code:`"EUR"`, :code:`"CAD"`, :code:`"AUD"`, :code:`"JPY"`,
            :code:`"CHF"`, :code:`"MXN"`, :code:`"BRL"`, :code:`"NZD"`,
            :code:`"SEK"`, :code:`"ZAR"`.

        Returns
        -------
        listing : dict[str, Any]
            Discogs content metadata for the listing.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "allow_offers": <bool>,
                    "audio": <bool>,
                    "comments": <str>,
                    "condition": <str>,
                    "id": <int>,
                    "original_price": {
                      "curr_abbr": <str>,
                      "curr_id": <int>,
                      "formatted": <str>,
                      "value": <float>
                    },
                    "original_shipping_price": {
                      "curr_abbr": <str>,
                      "curr_id": <int>,
                      "formatted": <str>,
                      "value": <float>
                    },
                    "posted": <str>,
                    "price": {
                      "currency": <str>,
                      "value": <int>
                    },
                    "release": {
                      "catalog_number": <str>,
                      "description": <str>,
                      "id": <int>,
                      "resource_url": <str>,
                      "thumbnail": <str>,
                      "year": <int>
                    },
                    "resource_url": <str>,
                    "seller": {
                      "avatar_url": <str>,
                      "payment": <str>,
                      "resource_url": <str>,
                      "shipping": <str>,
                      "stats": {
                        "rating": <str>,
                        "stars": <float>,
                        "total": <int>
                      },
                      "url": <str>,
                      "username": <str>
                    },
                    "shipping_price": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "ships_from": <str>,
                    "sleeve_condition": <str>,
                    "status": <str>,
                    "uri": <str>
                  }
        """
        self._validate_number("listing_id", listing_id, int, 1)
        params = {}
        if currency is not None:
            currency = self._prepare_string("currency", currency).upper()
            if currency not in self._CURRENCIES:
                raise ValueError(
                    f"Invalid currency {currency!r}. "
                    f"Valid values: {self._join_values(self._CURRENCIES)}."
                )
            params["curr_abbr"] = currency
        return self._client._request(
            "GET", f"marketplace/listings/{listing_id}", params=params
        ).json()

    def create_listing(
        self,
        release_id: int | str,
        /,
        media_condition: str,
        price: float,
        *,
        allow_offers: bool | None = None,
        private_notes: str | None = None,
        public_notes: str | None = None,
        status: str | None = None,
        shipping_count: float | str | None = None,
        storage_location: str | None = None,
        sleeve_condition: str | None = None,
        weight: float | str | None = None,
    ) -> dict[str, Any]:
        """
        `Marketplace > New Listing <https://www.discogs.com/developers
        /#page:marketplace,header:marketplace-new-listing>`_: Create a
        marketplace listing.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`772347`, :code:`"7781525"`.

        media_condition : str
            Media condition.

            **Valid values**: :code:`"Mint (M)"`,
            :code:`"Near Mint (NM or M-)"`,
            :code:`"Very Good Plus (VG+)"`, :code:`"Very Good (VG)"`,
            :code:`"Good Plus (G+)"`, :code:`"Good (G)"`,
            :code:`"Fair (F)"`, :code:`"Poor (P)"`.

        price : float
            Listing price.

        allow_offers : bool; keyword-only; optional
            Whether to accept offers for the listed item.

            **API default**: :code:`False`.

        private_notes : str; keyword-only; optional
            Private comments (e.g., external IDs) that are visible to
            only the seller.

        public_notes : str; keyword-only; optional
            Public comments (e.g., item condition) that are displayed to
            the buyers.

        status : str; keyword-only; optional
            Listing status.

            **Valid values**: :code:`"Draft"`, :code:`"For Sale"`.

            **API default**: :code:`"For Sale"`.

        shipping_count : float or str; keyword-only; optional
            Number of items the listing counts as for the purpose of
            calculating the shipping cost. Use :code:`"auto"` to
            automatically estimate the quantity.

            **API default**: :code:`"auto"`.

        storage_location : str; keyword-only; optional
            Identifier for the item's physical storage location that is
            visible to only the seller.

        sleeve_condition : str; keyword-only; optional
            Sleeve condition.

            **Valid values**: :code:`"Mint (M)"`,
            :code:`"Near Mint (NM or M-)"`,
            :code:`"Very Good Plus (VG+)"`, :code:`"Very Good (VG)"`,
            :code:`"Good Plus (G+)"`, :code:`"Good (G)"`,
            :code:`"Fair (F)"`, :code:`"Poor (P)"`, :code:`"Generic"`,
            :code:`"Not Graded"`, :code:`"No Cover"`.

        weight : float or str; keyword-only; optional
            Weight of the item in grams for the purpose of calculating
            the shipping cost. Use :code:`"auto"` to automatically
            estimate the value.

            **API default**: :code:`"auto"`.

        Returns
        -------
        listing : dict[str, Any]
            Discogs content metadata for the newly created listing.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "listing_id": <int>,
                    "resource_url": <str>
                  }
        """
        self._client._require_authentication("marketplace.create_listing")
        self._validate_number("release_id", release_id, int, 1)
        return self._upsert_listing(
            allow_offers=allow_offers,
            media_condition=media_condition,
            price=price,
            private_notes=private_notes,
            public_notes=public_notes,
            status=status,
            shipping_count=shipping_count,
            storage_location=storage_location,
            sleeve_condition=sleeve_condition,
            weight=weight,
            payload={"release_id": release_id},
        )

    def update_listing(
        self,
        listing_id: int | str,
        /,
        *,
        allow_offers: bool | None = None,
        media_condition: str | None = None,
        price: float | None = None,
        private_notes: str | None = None,
        public_notes: str | None = None,
        status: str | None = None,
        shipping_count: float | str | None = None,
        storage_location: str | None = None,
        sleeve_condition: str | None = None,
        weight: float | str | None = None,
    ) -> None:
        """
        `Marketplace > Listing > Edit A Listing <https://www.discogs.com
        /developers/#page:marketplace,
        header:marketplace-listing-post>`_: Update a marketplace
        listing.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        listing_id : int or str; positional-only
            Discogs ID of the listing.

            **Examples**: :code:`172723812`, :code:`"2983532888"`.

        allow_offers : bool; keyword-only; optional
            Whether to accept offers for the listed item.

            **API default**: :code:`False`.

        media_condition : str; keyword-only; optional
            Media condition.

            **Valid values**: :code:`"Mint (M)"`,
            :code:`"Near Mint (NM or M-)"`,
            :code:`"Very Good Plus (VG+)"`, :code:`"Very Good (VG)"`,
            :code:`"Good Plus (G+)"`, :code:`"Good (G)"`,
            :code:`"Fair (F)"`, :code:`"Poor (P)"`.

        price : float; keyword-only; optional
            Listing price.

        private_notes : str; keyword-only; optional
            Private comments (e.g., external IDs) that are visible to
            only the seller.

        public_notes : str; keyword-only; optional
            Public comments (e.g., item condition) that are displayed to
            the buyers.

        status : str; keyword-only; optional
            Listing status.

            **Valid values**: :code:`"Draft"`, :code:`"For Sale"`.

        shipping_count : float or str; keyword-only; optional
            Number of items the listing counts as for the purpose of
            calculating the shipping cost. Use :code:`"auto"` to
            automatically estimate the quantity.

        storage_location : str; keyword-only; optional
            Identifier for the item's physical storage location that is
            visible to only the seller.

        sleeve_condition : str; keyword-only; optional
            Sleeve condition.

            **Valid values**: :code:`"Mint (M)"`,
            :code:`"Near Mint (NM or M-)"`,
            :code:`"Very Good Plus (VG+)"`, :code:`"Very Good (VG)"`,
            :code:`"Good Plus (G+)"`, :code:`"Good (G)"`,
            :code:`"Fair (F)"`, :code:`"Poor (P)"`, :code:`"Generic"`,
            :code:`"Not Graded"`, :code:`"No Cover"`.

        weight : float or str; keyword-only; optional
            Weight of the item in grams for the purpose of calculating
            the shipping cost. Use :code:`"auto"` to automatically
            estimate the value.
        """
        self._client._require_authentication("marketplace.update_listing")
        self._validate_number("listing_id", listing_id, int, 1)
        return self._upsert_listing(
            f"/{listing_id}",
            allow_offers=allow_offers,
            media_condition=media_condition,
            price=price,
            private_notes=private_notes,
            public_notes=public_notes,
            status=status,
            shipping_count=shipping_count,
            storage_location=storage_location,
            sleeve_condition=sleeve_condition,
            weight=weight,
        )

    def delete_listing(self, listing_id: int | str, /) -> None:
        """
        `Marketplace > Listing > Delete A Listing
        <https://www.discogs.com/developers/#page:marketplace,
        header:marketplace-listing-delete>`_: Delete a marketplace
        listing.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        listing_id : int or str; positional-only
            Discogs ID of the listing.

            **Examples**: :code:`172723812`, :code:`"2983532888"`.
        """
        self._client._require_authentication("marketplace.delete_listing")
        self._validate_number("listing_id", listing_id, int, 1)
        self._client._request("DELETE", f"marketplace/listings/{listing_id}")

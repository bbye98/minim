from datetime import datetime
from typing import Any

from ..._shared import TTLCache
from ._shared import DiscogsResourceAPI


class MarketplaceAPI(DiscogsResourceAPI):
    """
    Marketplace API endpoints for the Discogs API.

    .. important::

       This class is managed by
       :class:`~minim.api.discogs.DiscogsAPIClient` and should not be
       instantiated directly.
    """

    _LISTING_SORT_FIELDS = {
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
    _USER_LISTING_STATUSES = {"Draft", "For Sale"}
    _FILTER_LISTING_STATUSES = {
        "All",
        "Deleted",
        "Expired",
        "Sold",
        "Suspended",
        "Violation",
    }
    _ORDER_SORT_FIELDS = {"id", "buyer", "created", "status", "last_activity"}
    _USER_ORDER_STATUSES = {
        "New Order",
        "Buyer Contacted",
        "Invoice Sent",
        "Payment Pending",
        "Payment Received",
        "In Progress",
        "Shipped",
        "Refund Sent",
        "Cancelled (Non-Paying Buyer)",
        "Cancelled (Item Unavailable)",
        "Cancelled (Per Buyer's Request)",
    }
    _FILTER_ORDER_STATUSES = {
        "All",
        "Merged",
        "Order Changed",
        "Cancelled",
        "Cancelled (Refund Received)",
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
        shipping_count: int | str | None = None,
        storage_location: str | None = None,
        sleeve_condition: str | None = None,
        weight: int | str | None = None,
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

        shipping_count : int or str; keyword-only; optional
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

        weight : int or str; keyword-only; optional
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

               .. code-block::

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
            if status not in self._USER_LISTING_STATUSES:
                raise ValueError(
                    f"Invalid listing status {status!r}. Valid values: "
                    f"{self._join_values(self._USER_LISTING_STATUSES)}."
                )
            payload["status"] = status
        if shipping_count is not None:
            if shipping_count != "auto":
                self._validate_number("shipping_count", shipping_count, int, 0)
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
                | self._ADDITIONAL_SLEEVE_CONDITIONS
            ):
                raise ValueError(
                    f"Invalid sleeve condition {sleeve_condition!r}. "
                    f"Valid values: {self._join_values(conditions)}."
                )
            payload["sleeve_condition"] = sleeve_condition
        if weight is not None:
            if weight != "auto":
                self._validate_number("weight", weight, int, 0)
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
        catalog information for a user's marketplace listings.

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
        listings : dict[str, Any]
            Page of Discogs content metadata for the seller's inventory.

            .. admonition:: Sample responses
               :class: response dropdown

               .. code-block::

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
                statuses := self._FILTER_LISTING_STATUSES
                | self._USER_LISTING_STATUSES
            ):
                raise ValueError(
                    f"Invalid listing status {status!r}. "
                    f"Valid values: {self._join_values(statuses)}."
                )
        if sort_by is not None:
            sort_by = self._prepare_string("sort_by", sort_by).lower()
            if sort_by not in self._LISTING_SORT_FIELDS:
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid values: "
                    f"{self._join_values(self._LISTING_SORT_FIELDS)}."
                )

            if sort_by in {"status", "location"}:
                self._client._require_authentication(
                    "marketplace.get_user_inventory"
                )
            params["sort"] = sort_by
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

               .. code-block::

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
                      "value": <float>
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
        self._validate_numeric("listing_id", listing_id, int, 1)
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
        shipping_count: int | str | None = None,
        storage_location: str | None = None,
        sleeve_condition: str | None = None,
        weight: int | str | None = None,
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

        shipping_count : int or str; keyword-only; optional
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

        weight : int or str; keyword-only; optional
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

               .. code-block::

                  {
                    "listing_id": <int>,
                    "resource_url": <str>
                  }
        """
        self._client._require_authentication("marketplace.create_listing")
        self._validate_numeric("release_id", release_id, int, 1)
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
        shipping_count: int | str | None = None,
        storage_location: str | None = None,
        sleeve_condition: str | None = None,
        weight: int | str | None = None,
    ) -> None:
        """
        `Marketplace > Listing > Edit a Listing <https://www.discogs.com
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

        shipping_count : int or str; keyword-only; optional
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

        weight : int or str; keyword-only; optional
            Weight of the item in grams for the purpose of calculating
            the shipping cost. Use :code:`"auto"` to automatically
            estimate the value.
        """
        self._client._require_authentication("marketplace.update_listing")
        self._validate_numeric("listing_id", listing_id, int, 1)
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
        `Marketplace > Listing > Delete a Listing
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
        self._validate_numeric("listing_id", listing_id, int, 1)
        self._client._request("DELETE", f"marketplace/listings/{listing_id}")

    @TTLCache.cached_method(ttl="user")
    def get_order(self, order_id: str, /) -> dict[str, Any]:
        """
        `Marketplace > Order > Get Order <https://www.discogs.com
        /developers/#page:marketplace,header:marketplace-order>`_: Get
        Discogs catalog information for a marketplace order.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        order_id : str; positional-only
            Discogs ID of the order.

            **Example**: :code:`"1-1"`.

        Returns
        -------
        order : dict[str, Any]
            Discogs content metadata for the order.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "additional_instructions": <str>,
                    "archived": <bool>,
                    "buyer": {
                      "id": <int>,
                      "resource_url": <str>,
                      "username": <str>
                    },
                    "created": <str>,
                    "fee": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "id": <str>,
                    "items": [
                      {
                        "id": <int>,
                        "media_condition": <str>,
                        "price": {
                          "currency": <str>,
                          "value": <float>
                        },
                        "release": {
                          "description": <str>,
                          "id": <int>
                        },
                        "sleeve_condition": <str>
                      }
                    ],
                    "last_activity": <str>,
                    "messages_url": <str>,
                    "next_status": <list[str]>,
                    "resource_url": <str>,
                    "seller": {
                      "id": <int>,
                      "resource_url": <str>,
                      "username": <str>
                    },
                    "shipping": {
                      "currency": <str>,
                      "method": <str>,
                      "value": <float>
                    },
                    "shipping_address": <str>,
                    "status": <str>,
                    "total": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "uri": <str>
                  }
        """
        self._client._require_authentication("marketplace.get_order")
        return self._client._request(
            "GET",
            f"marketplace/orders/{self._prepare_string('order_id', order_id)}",
        ).json()

    def update_order(
        self,
        order_id: str,
        /,
        *,
        status: str | None = None,
        shipping_fee: float | None = None,
    ) -> dict[str, Any]:
        """
        `Marketplace > Order > Edit an Order <https://www.discogs.com
        /developers/#page:marketplace,header:marketplace-order-post>`_:
        Update a marketplace order.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        .. important::

           Exactly one of `status` or `shipping_fee` must be provided.

        .. note::

           Calling this method will send the buyer a message with the
           following content:

           .. code-block:: none

              Seller changed status from {old_status} to {new_status}

        .. seealso::

           :meth:`add_order_message` – Simultaneously add an order
           message and change the order status.

        Parameters
        ----------
        order_id : str; positional-only
            Discogs ID of the order.

            **Example**: :code:`"1-1"`.

        status : str; keyword-only; optional
            Order status.

            **Valid values**: :code:`"New Order"`,
            :code:`"Buyer Contacted"`, :code:`"Invoice Sent"`,
            :code:`"Payment Pending"`, :code:`"Payment Received"`,
            :code:`"In Progress"`, :code:`"Shipped"`,
            :code:`"Refund Sent"`,
            :code:`"Cancelled (Non-Paying Buyer)"`,
            :code:`"Cancelled (Item Unavailable)"`,
            :code:`"Cancelled (Per Buyer's Request)"`.

        shipping_fee : float; keyword-only; optional
            Shipping fee. If specified, the buyer is invoiced and the
            order status is set to :code:`Invoice Sent`.

        Returns
        -------
        order : dict[str, Any]
            Discogs content metadata for the updated order.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "additional_instructions": <str>,
                    "archived": <bool>,
                    "buyer": {
                      "id": <int>,
                      "resource_url": <str>,
                      "username": <str>
                    },
                    "created": <str>,
                    "fee": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "id": <str>,
                    "items": [
                      {
                        "id": <int>,
                        "media_condition": <str>,
                        "price": {
                          "currency": <str>,
                          "value": <float>
                        },
                        "release": {
                          "description": <str>,
                          "id": <int>
                        },
                        "sleeve_condition": <str>
                      }
                    ],
                    "last_activity": <str>,
                    "messages_url": <str>,
                    "next_status": <list[str]>,
                    "resource_url": <str>,
                    "seller": {
                      "id": <int>,
                      "resource_url": <str>,
                      "username": <str>
                    },
                    "shipping": {
                      "currency": <str>,
                      "method": <str>,
                      "value": <float>
                    },
                    "shipping_address": <str>,
                    "status": <str>,
                    "total": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "uri": <str>
                  }
        """
        self._client._require_authentication("marketplace.update_order")
        payload = {}
        if status is not None:
            status = self._prepare_string("status", status).capitalize()
            if status not in self._USER_ORDER_STATUSES:
                raise ValueError(
                    f"Invalid order status {status!r}. Valid values: "
                    f"{self._join_values(self._USER_ORDER_STATUSES)}."
                )
            payload["status"] = status
        if shipping_fee is not None:
            self._validate_number("shipping_fee", shipping_fee, int | float, 0)
            payload["shipping"] = shipping_fee
        if len(payload) != 1:
            raise ValueError(
                "Exactly one of `status` or `shipping_fee` must be provided."
            )
        return self._client._request(
            "POST",
            f"marketplace/orders/{self._prepare_string('order_id', order_id)}",
            json=payload,
        ).json()

    @TTLCache.cached_method(ttl="user")
    def get_my_orders(
        self,
        *,
        status: str | None = None,
        created_after: str | datetime | None = None,
        created_before: str | datetime | None = None,
        archived: bool | None = None,
        limit: int | None = None,
        page: int | None = None,
        sort_by: str | None = None,
        descending: bool | None = None,
    ) -> dict[str, Any]:
        """
        `Marketplace > List Orders <https://www.discogs.com/developers
        /#page:marketplace,header:marketplace-list-orders>`_: Get
        Discogs catalog information for the current user's marketplace
        orders.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        status : str; keyword-only; optional
            Order status to filter by.

            **Valid values**: :code:`"All"`, :code:`"New Order"`,
            :code:`"Buyer Contacted"`, :code:`"Invoice Sent"`,
            :code:`"Payment Pending"`, :code:`"Payment Received"`,
            :code:`"In Progress"`, :code:`"Shipped"`, :code:`"Merged"`,
            :code:`"Order Changed"`, :code:`"Refund Sent"`,
            :code:`"Cancelled (Non-Paying Buyer)"`,
            :code:`"Cancelled (Item Unavailable)"`,
            :code:`"Cancelled (Per Buyer's Request)"`,
            :code:`"Cancelled (Refund Received)"`.

        created_after : str or datetime.datetime; keyword-only; optional
            Only return orders created after this date, in
            :code:`YYYY-MM-DDTHH:MM:SSZ` format.

        created_before : str or datetime.datetime; keyword-only; \
        optional
            Only return orders created before this date, in
            :code:`YYYY-MM-DDTHH:MM:SSZ` format.

        archived : bool; keyword-only; optional
            Whether to only include archived orders.

        limit : int; keyword-only; optional
            Maximum number of orders to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            orders.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        sort_by : str; keyword-only; optional
            Field to sort the returned orders by.

            **Valid values**: :code:`"id"`, :code:`"buyer"`,
            :code:`"created"`, :code:`"status"`,
            :code:`"last_activity"`.

        descending : bool; keyword-only; optional
            Whether to sort in descending order.

        Returns
        -------
        orders : dict[str, Any]
            Page of Discogs content metadata for the current user's
            orders.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "orders": [
                      {
                        "additional_instructions": <str>,
                        "archived": <bool>,
                        "buyer": {
                          "id": <int>,
                          "resource_url": <str>,
                          "username": <str>
                        },
                        "created": <str>,
                        "fee": {
                          "currency": <str>,
                          "value": <float>
                        },
                        "id": <str>,
                        "items": [
                          {
                            "id": <int>,
                            "media_condition": <str>,
                            "price": {
                              "currency": <str>,
                              "value": <float>
                            },
                            "release": {
                              "description": <str>,
                              "id": <int>
                            },
                            "sleeve_condition": <str>
                          }
                        ],
                        "last_activity": <str>,
                        "messages_url": <str>,
                        "next_status": <list[str]>,
                        "resource_url": <str>,
                        "seller": {
                          "id": <int>,
                          "resource_url": <str>,
                          "username": <str>
                        },
                        "shipping": {
                          "currency": <str>,
                          "method": <str>,
                          "value": <float>
                        },
                        "shipping_address": <str>,
                        "status": <str>,
                        "total": {
                          "currency": <str>,
                          "value": <float>
                        },
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
        self._client._require_authentication("marketplace.get_my_orders")
        params = {}
        if status is not None:
            status = self._prepare_string("status", status).capitalize()
            if status not in (
                order_statuses := self._USER_ORDER_STATUSES
                | self._FILTER_ORDER_STATUSES
            ):
                raise ValueError(
                    f"Invalid order status {status!r}. Valid values: "
                    f"{self._join_values(order_statuses)}."
                )
            params["status"] = status
        if created_after is not None:
            params["created_after"] = self._prepare_datetime(
                created_after, "%Y-%m-%dT%H:%M:%SZ"
            )
        if created_before is not None:
            params["created_before"] = self._prepare_datetime(
                created_before, "%Y-%m-%dT%H:%M:%SZ"
            )
        if archived is not None:
            self._validate_type("archived", archived, bool)
            params["archived"] = archived
        if sort_by is not None:
            sort_by = self._prepare_string("sort_by", sort_by).lower()
            if sort_by not in self._ORDER_SORT_FIELDS:
                raise ValueError(
                    f"Invalid sort field {sort_by!r}. Valid values: "
                    f"{self._join_values(self._ORDER_SORT_FIELDS)}."
                )
            params["sort"] = sort_by
        if descending is not None:
            self._validate_type("descending", descending, bool)
            params["sort_order"] = "desc" if descending else "asc"
        return self._get_paginated_resources(
            "marketplace/orders", limit=limit, page=page, params=params
        )

    @TTLCache.cached_method(ttl="user")
    def get_order_messages(
        self,
        order_id: str,
        /,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        `Marketplace > List Order Messages > List Order Messages
        <https://www.discogs.com/developers/#page:marketplace,
        header:marketplace-list-order-messages-get>`_: Get Discogs
        content metadata for a marketplace order's messages.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        order_id : str; positional-only
            Discogs ID of the order.

            **Example**: :code:`"1-1"`.

        limit : int; keyword-only; optional
            Maximum number of messages to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            messages.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        messages : dict[str, Any]
            Page of Discogs content metadata for the order's messages.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "from": {
                      "resource_url": <str>,
                      "username": <str>
                    },
                    "message": <str>,
                    "order": {
                      "id": <str>,
                      "resource_url": <str>
                    },
                    "subject": <str>,
                    "timestamp": <str>
                  }
        """
        self._client._require_authentication("marketplace.get_order_messages")
        return self._get_paginated_resources(
            "marketplace/orders"
            f"/{self._prepare_string('order_id', order_id)}/messages",
            limit=limit,
            page=page,
        )

    def add_order_message(
        self,
        order_id: str,
        message: str | None = None,
        /,
        *,
        status: str | None = None,
    ) -> dict[str, Any]:
        """
        `Marketplace > List Order Messages > Add New Message
        <https://www.discogs.com/developers/#page:marketplace,
        header:marketplace-list-order-messages-post>`_: Add a
        marketplace order message.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        .. important::

           At least one of `message` or `status` must be provided.

        Parameters
        ----------
        order_id : str; positional-only
            Discogs ID of the order.

            **Example**: :code:`"1-1"`.

        message : str; positional-only; optional
            Order message.

        status : str; keyword-only; optional
            Order status.

            .. note::

               If specified, `message` will be prepended with:

               .. code-block:: none

                  Seller changed status from {old_status} to {new_status}

            **Valid values**: :code:`"New Order"`,
            :code:`"Buyer Contacted"`, :code:`"Invoice Sent"`,
            :code:`"Payment Pending"`, :code:`"Payment Received"`,
            :code:`"In Progress"`, :code:`"Shipped"`,
            :code:`"Refund Sent"`,
            :code:`"Cancelled (Non-Paying Buyer)"`,
            :code:`"Cancelled (Item Unavailable)"`,
            :code:`"Cancelled (Per Buyer's Request)"`.

        Returns
        -------
        message : dict[str, Any]
            Discogs content metadata for the order message.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "from": {
                      "resource_url": <str>,
                      "username": <str>
                    },
                    "message": <str>,
                    "order": {
                      "id": <str>,
                      "resource_url": <str>
                    },
                    "subject": <str>,
                    "timestamp": <str>
                  }
        """
        self._client._require_authentication("marketplace.add_order_message")
        payload = {}
        if message is not None:
            self._validate_type("message", message, str)
            payload["message"] = message
        if status is not None:
            status = self._prepare_string("status", status).capitalize()
            if status not in self._USER_ORDER_STATUSES:
                raise ValueError(
                    f"Invalid order status {status!r}. Valid values: "
                    f"{self._join_values(self._USER_ORDER_STATUSES)}."
                )
            payload["status"] = status
        if not payload:
            raise RuntimeError(
                "At least one of `message` or `status` must be provided."
            )
        return self._client._request(
            "POST",
            f"marketplace/order/{self._prepare_string('order_id', order_id)}/messages",
            json=payload,
        ).json()

    @TTLCache.cached_method(ttl="static")
    def get_selling_fee(
        self, price: float, /, currency: str | None = None
    ) -> dict[str, Any]:
        """
        `Marketplace > Fee <https://www.discogs.com/developers
        /#page:marketplace,header:marketplace-fee>`_: Get the fee for
        selling an item on the marketplace at a given price․
        `Marketplace > Fee with Currency <https://www.discogs.com
        /developers/#page:marketplace,
        header:marketplace-fee-with-currency>`_: Get the fee in a
        particular currency for selling an item on the marketplace at a
        given price.

        Parameters
        ----------
        price : float; positional-only
            Item price.

        currency : str; optional
            Fee currency.

            **Valid values**: :code:`"USD"`, :code:`"GBP"`,
            :code:`"EUR"`, :code:`"CAD"`, :code:`"AUD"`, :code:`"JPY"`,
            :code:`"CHF"`, :code:`"MXN"`, :code:`"BRL"`, :code:`"NZD"`,
            :code:`"SEK"`, :code:`"ZAR"`.

        Returns
        -------
        fee : dict[str, Any]
            Fee.

            **Sample response**:
            :code:`{"currency": <str>, "value": <float>}`.
        """
        self._validate_number("price", price, int | float, 0)
        if currency is None:
            return self._client._request(f"marketplace/fee/{price}").json()
        currency = self._prepare_string("currency", currency).upper()
        if currency not in self._CURRENCIES:
            raise ValueError(
                f"Invalid currency {currency!r}. "
                f"Valid values: {self._join_values(self._CURRENCIES)}."
            )
        return self._client._request(
            f"marketplace/fee/{price}/{currency}"
        ).json()

    @TTLCache.cached_method(ttl="popularity")
    def get_release_price_suggestions(
        self, release_id: int | str, /
    ) -> dict[str, Any]:
        """
        `Marketplace > Price Suggestions <https://www.discogs.com
        /developers/#page:marketplace,
        header:marketplace-price-suggestions>`_: Get suggested pricing
        information for a release.

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

        Returns
        -------
        price_suggestions : dict[str, Any]
            Suggested prices for the release.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "Very Good (VG)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Good Plus (G+)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Near Mint (NM or M-)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Good (G)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Very Good Plus (VG+)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Mint (M)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Fair (F)": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "Poor (P)": {
                      "currency": <str>,
                      "value": <float>
                    }
                  }
        """
        self._client._require_authentication(
            "marketplace.get_release_price_suggestions"
        )
        self._validate_numeric("release_id", release_id, int, 1)
        return self._client._request(
            "GET", f"marketplace/price_suggestions/{release_id}"
        ).json()

    @TTLCache.cached_method(ttl="popularity")
    def get_release_marketplace_stats(
        self, release_id: int | str, /, *, currency: str | None = None
    ) -> dict[str, Any]:
        """
        `Marketplace > Release Statistics <https://www.discogs.com
        /developers/#page:marketplace,
        header:marketplace-release-statistics>`_: Get a release's
        marketplace statistics.

        Parameters
        ----------
        release_id : int or str; positional-only
            Discogs ID of the release.

            **Examples**: :code:`772347`, :code:`"7781525"`.

        currency : str; keyword-only; optional
            Currency.

            **Valid values**: :code:`"USD"`, :code:`"GBP"`,
            :code:`"EUR"`, :code:`"CAD"`, :code:`"AUD"`, :code:`"JPY"`,
            :code:`"CHF"`, :code:`"MXN"`, :code:`"BRL"`, :code:`"NZD"`,
            :code:`"SEK"`, :code:`"ZAR"`.

        Returns
        -------
        marketplace_stats : dict[str, Any]
            Release's marketplace statistics.

            .. admonition:: Sample response
               :class: response dropdown

               .. code-block::

                  {
                    "blocked_from_sale": <bool>,
                    "lowest_price": {
                      "currency": <str>,
                      "value": <float>
                    },
                    "num_for_sale": <int>
                  }
        """
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
            f"marketplace/stats/{release_id}", params=params
        ).json()

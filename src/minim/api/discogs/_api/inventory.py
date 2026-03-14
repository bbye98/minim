import csv
from email.message import Message
import io
from pathlib import Path
from typing import Any, IO

from ..._shared import TTLCache
from ._shared import DiscogsResourceAPI


class InventoryAPI(DiscogsResourceAPI):
    """
    Inventory Export and Inventory Upload API endpoints for the Discogs
    API.

    .. important::

       This class is managed by
       :class:`minim.api.discogs.DiscogsAPIClient` and should not be
       instantiated directly.
    """

    def _prepare_inventory_csv(
        self,
        inventory_csv: bytes | str | Path,
        /,
        *,
        required_fields: set[str],
        optional_fields: set[str],
        update: bool = False,
    ) -> tuple[str, IO[bytes], str]:
        """
        Validate and prepare the inventory comma-separated values (CSV)
        payload.

        Parameters
        ----------
        inventory_csv : bytes, str, or pathlib.Path; positional-only
            Path to, name of, or contents of an inventory CSV file.

        required_fields : set[str]; keyword-only
            Required fields.

        optional_fields : set[str]; keyword-only
            Optional or other allowable fields.

        update : bool; keyword-only; default: :code:`False`
            Whether the CSV is for an inventory update and one of the
            optional fields is required.

        Returns
        -------
        filename : str
            CSV filename or :code:`"inventory.csv"` if a byte string is
            provided instead.

        obj : io.BufferedReader or io.BytesIO
            Binary stream of the CSV file or the user-provided byte
            string.

        content_type : str
            Content type (:code:`"text/csv"`).
        """
        self._validate_type("inventory_csv", inventory_csv, bytes | str | Path)
        if (is_str := isinstance(inventory_csv, str)) or isinstance(
            inventory_csv, bytes
        ):
            inventory_csv = self._prepare_string(
                "inventory_csv", inventory_csv
            )
            if is_str:
                try:
                    inventory_csv = (
                        Path(inventory_csv).expanduser().resolve(True)
                    )
                except (FileNotFoundError, OSError):
                    pass

        if isinstance(inventory_csv, Path):
            csv_filename = inventory_csv.name
            csv_obj = inventory_csv.open("rb")
        else:
            csv_filename = "inventory.csv"
            csv_obj = io.BytesIO(
                inventory_csv.encode("utf-8")
                if isinstance(inventory_csv, str)
                else inventory_csv
            )

        csv_stream = io.TextIOWrapper(csv_obj)
        try:
            csv_reader = csv.DictReader(csv_stream)
            csv_headers = set(csv_reader.fieldnames or [])
            if missing_fields := required_fields - csv_headers:
                raise ValueError(
                    "`inventory_csv` is missing the following required "
                    f"field(s): {self._join_values(missing_fields)}."
                )
            additional_fields = csv_headers - required_fields
            if update and not additional_fields:
                raise ValueError(
                    "`inventory_csv` must have at least one optional "
                    "field for an inventory update."
                )
            if extra_fields := additional_fields - optional_fields:
                raise ValueError(
                    "`inventory_csv` has the following extra or unsupported "
                    f"field(s): {self._join_values(extra_fields)}."
                )

            all_conditions = (
                self._CONDITIONS | self._ADDITIONAL_SLEEVE_CONDITIONS
            )
            for row in csv_reader:
                for key, value in row.items():
                    if value is not None or key in required_fields:
                        match key:
                            case "release_id" | "weight" | "format_quantity":
                                self._validate_numeric(key, value, int, 0)
                            case "price":
                                self._validate_numeric(key, value, float, 0)
                            case "media_condition":
                                self._validate_type(key, value, str)
                                if value not in self._CONDITIONS:
                                    raise ValueError(
                                        f"Invalid media condition {value!r}. "
                                        f"Valid values: {self._join_values(self._CONDITIONS)}."
                                    )
                            case "sleeve_condition":
                                self._validate_type(key, value, str)
                                if value not in all_conditions:
                                    raise ValueError(
                                        f"Invalid media condition {value!r}. "
                                        f"Valid values: {self._join_values(all_conditions)}."
                                    )
                            case "comments" | "external_id" | "location":
                                self._validate_type(key, value, str)
                            case "accept_offer":
                                self._validate_type(key, value, str)
                                if value not in {"N", "Y"}:
                                    raise ValueError(
                                        "Invalid `accept_offer` value "
                                        f"{value!r}. Valid values: 'N', 'Y'."
                                    )
        finally:
            csv_stream.detach()
            csv_obj.seek(0)

        return csv_filename, csv_obj, "text/csv"

    def export_my_inventory(self) -> str:
        """
        `Inventory Export > Export Your Inventory
        <https://www.discogs.com/developers/#page:inventory-export,
        header:inventory-export-export-your-inventory>`_: Export the
        current user's inventory as comma-separated values (CSV).

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Returns
        -------
        request_url : str
            Request URL to get Discogs content metadata for the
            inventory export.

            .. seealso::

               :meth:`get_inventory_export` – Get information for an
               inventory export.

               :meth:`download_inventory_export` – Download an inventory
               export CSV.
        """
        self._client._require_authentication("inventory.export_my_inventory")
        return self._client._request("POST", "inventory/export").headers[
            "location"
        ]

    @TTLCache.cached_method(ttl="user")
    def get_my_recent_inventory_exports(
        self, *, limit: int | None = None, page: int | None = None
    ) -> dict[str, Any]:
        """
        `Inventory Export > Get Recent Exports <https://www.discogs.com
        /developers/#page:inventory-export,
        header:inventory-export-get-recent-exports>`_: Get Discogs
        catalog information for the current user's recent inventory
        exports.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        limit : int; keyword-only; optional
            Maximum number of exports to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            exports.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        exports : dict[str, Any]
            Page of Discogs content metadata for the current user's
            recent inventory exports.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "id": <int>,
                        "created_ts": <str>,
                        "download_url": <str>,
                        "filename": <str>,
                        "finished_ts": <str>,
                        "status": <str>,
                        "url": <str>,
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
        self._client._require_authentication(
            "inventory.get_my_recent_inventory_exports"
        )
        return self._get_paginated_resources(
            "inventory/export", limit=limit, page=page
        )

    @TTLCache.cached_method(ttl="user")
    def get_inventory_export(self, export_id: int | str, /) -> dict[str, Any]:
        """
        `Inventory > Get an Export <https://www.discogs.com/developers
        /#page:inventory-export,header:inventory-export-get-an-export>`_:
        Get Discogs catalog information for an inventory export.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        export_id : int or str; positional-only
            Discogs ID of the export.

            **Examples**: :code:`599632`, :code:`"16105411"`.

        Returns
        -------
        export : dict[str, Any]
            Discogs content metadata for an inventory export.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "id": <int>,
                    "created_ts": <str>,
                    "download_url": <str>,
                    "filename": <str>,
                    "finished_ts": <str>,
                    "status": <str>,
                    "url": <str>,
                  }
        """
        self._client._require_authentication("inventory.get_inventory_export")
        self._validate_number("export_id", export_id, int, 1)
        return self._client._request(
            "GET", f"inventory/export/{export_id}"
        ).json()

    @TTLCache.cached_method(ttl="user")
    def download_inventory_export(
        self, export_id: int | str, /, *, target: str | Path | None = None
    ) -> bytes | Path:
        """
        `Inventory Export > Download an Export <https://www.discogs.com
        /developers/#page:inventory-export,
        header:inventory-export-download-an-export>`_: Download the
        comma-separated values (CSV) for an inventory export.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        export_id : int or str; positional-only
            Discogs ID of the export.

            **Examples**: :code:`599632`, :code:`"16105411"`.

        target : str or pathlib.Path; keyword-only; optional
            Target directory or file. If provided, a CSV file is
            written in the specified folder or with the specified
            filename. Otherwise, the raw CSV data is returned.

        Returns
        -------
        export_csv : bytes or pathlib.Path
            Raw CSV data or absolute path to the written CSV file for
            the inventory export.
        """
        self._client._require_authentication(
            "inventory.download_inventory_export"
        )
        self._validate_number("export_id", export_id, int, 1)
        resp = self._client._request(
            "GET", f"inventory/export/{export_id}/download"
        )
        if target is None:
            return resp.content

        target = Path(target).expanduser().resolve()
        _msg = Message()
        _msg["content-disposition"] = resp.headers["content-disposition"]
        original_filename = Path(
            _msg.get_param("filename", header="content-disposition")
        )
        if target.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            target /= original_filename
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.suffix != original_filename.suffix:
                target = Path(f"{target}{original_filename.suffix}")
        with open(target, "w") as f:
            f.write(resp.content)
        return target

    def upload_inventory_additions(self, inventory_csv: str | Path, /) -> str:
        """
        `Inventory Upload > Add Inventory <https://www.discogs.com
        /developers/#page:inventory-upload,
        header:inventory-upload-add-inventory>`_: Add marketplace
        listings by uploading comma-separated values (CSV).

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        .. note::

           Listings are marked as "For Sale". Currency information is
           pulled from the current user's marketplace settings.

        Parameters
        ----------
        inventory_csv : str or pathlib.Path; positional-only
            Path to or name of a CSV file containing the listings to
            add.

            **Required fields**: :code:`release_id`, :code:`price`, and
            :code:`media_condition`.

            **Optional fields**: :code:`sleeve_condition`,
            :code:`comments`, :code:`accept_offer`, :code:`location`,
            :code:`external_id`, :code:`weight`, and
            :code:`format_quantity`.

        Returns
        -------
        upload_url : str
            Request URL to get Discogs content metadata for the
            inventory upload.

            .. seealso::

               :meth:`get_inventory_upload` – Get information for an
               inventory upload.
        """
        self._client._require_authentication(
            "inventory.upload_inventory_additions"
        )
        return self._client._request(
            "POST",
            "inventory/upload/add",
            files={
                "upload": self._prepare_inventory_csv(
                    inventory_csv,
                    required_fields={"release_id", "price", "media_condition"},
                    optional_fields={
                        "sleeve_condition",
                        "comments",
                        "accept_offer",
                        "location",
                        "external_id",
                        "weight",
                        "format_quantity",
                    },
                )
            },
        ).headers["Location"]

    def upload_inventory_updates(self, inventory_csv: str | Path, /) -> str:
        """
        `Inventory Upload > Change Inventory <https://www.discogs.com
        /developers/#page:inventory-upload,
        header:inventory-upload-change-inventory>`_: Update marketplace
        listings by uploading comma-separated values (CSV).

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        .. note::

           Currency information is pulled from the current user's
           marketplace settings.

        Parameters
        ----------
        inventory_csv : str or pathlib.Path; positional-only
            Path to or name of a CSV file containing the listings to
            update.

            **Required field**: :code:`release_id`.

            **Optional fields**: :code:`price`, :code:`media_condition`,
            :code:`sleeve_condition`, :code:`comments`,
            :code:`accept_offer`, :code:`location`, :code:`external_id`,
            :code:`weight`, and :code:`format_quantity`.

        Returns
        -------
        upload_url : str
            Request URL to get Discogs content metadata for the
            inventory upload.

            .. seealso::

               :meth:`get_inventory_upload` – Get information for an
               inventory upload.
        """
        self._client._require_authentication(
            "inventory.upload_inventory_updates"
        )
        return self._client._request(
            "POST",
            "inventory/upload/change",
            files={
                "upload": self._prepare_inventory_csv(
                    inventory_csv,
                    required_fields={"release_id"},
                    optional_fields={
                        "price",
                        "media_condition",
                        "sleeve_condition",
                        "comments",
                        "accept_offer",
                        "location",
                        "external_id",
                        "weight",
                        "format_quantity",
                    },
                    update=True,
                )
            },
        ).headers["Location"]

    def upload_inventory_deletions(self, inventory_csv: str | Path, /) -> str:
        """
        `Inventory Upload > Delete Inventory <https://www.discogs.com
        /developers/#page:inventory-upload,
        header:inventory-upload-delete-inventory>`_: Delete marketplace
        listings by uploading comma-separated values (CSV).

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        inventory_csv : str or pathlib.Path; positional-only
            Path to or name of a CSV file containing the listings to
            delete.

            **Required field**: :code:`listing_id`.

        Returns
        -------
        upload_url : str
            Request URL to get Discogs content metadata for the
            inventory upload.

            .. seealso::

               :meth:`get_inventory_upload` – Get information for an
               inventory upload.
        """
        self._client._require_authentication(
            "inventory.upload_inventory_deletions"
        )
        return self._client._request(
            "POST",
            "inventory/upload/delete",
            files={
                "upload": self._prepare_inventory_csv(
                    inventory_csv,
                    required_fields={"listing_id"},
                    optional_fields={},
                )
            },
        ).headers["Location"]

    @TTLCache.cached_method(ttl="user")
    def get_my_recent_inventory_uploads(
        self, *, limit: int | None = None, page: int | None = None
    ) -> dict[str, Any]:
        """
        `Inventory Upload > Get Recent Uploads <https://www.discogs.com
        /developers/#page:inventory-upload,
        header:inventory-upload-get-recent-uploads>`_: Get Discogs
        catalog information for the current user's recent inventory
        uploads.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        limit : int; keyword-only; optional
            Maximum number of uploads to return.

            **Valid range**: :code:`1` to :code:`100`.

            **API default**: :code:`50`.

        page : int; keyword-only; optional
            Page number. Use with `limit` to get the next page of
            uploads.

            **Minimum value**: :code:`1`.

            **API default**: :code:`1`.

        Returns
        -------
        uploads : dict[str, Any]
            Page of Discogs content metadata for the current user's
            recent inventory uploads.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "items": [
                      {
                        "created_ts": <str>,
                        "filename": <str>,
                        "finished_ts": <str>,
                        "id": <int>,
                        "results": <str>,
                        "status": <str>,
                        "type": <str>
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
        self._client._require_authentication(
            "inventory.get_my_recent_inventory_uploads"
        )
        return self._get_paginated_resources(
            "inventory/upload", limit=limit, page=page
        )

    @TTLCache.cached_method(ttl="user")
    def get_inventory_upload(self, upload_id: int | str, /) -> dict[str, Any]:
        """
        `Inventory Upload > Get an Upload <https://www.discogs.com
        /developers/#page:inventory-upload,
        header:inventory-upload-get-an-upload>`_: Get Discogs catalog
        information for an inventory upload.

        .. admonition:: User authentication
           :class: entitlement

           .. tab-set::

              .. tab-item:: Required

                 User authentication
                    Access protected endpoints.

        Parameters
        ----------
        upload_id : int or str; positional-only
            Discogs ID of the upload.

            **Examples**: :code:`119615`, :code:`"119615"`.

        Returns
        -------
        upload : dict[str, Any]
            Discogs content metadata for an inventory upload.

            .. admonition:: Sample response
               :class: response dropdown

               .. code::

                  {
                    "created_ts": <str>,
                    "filename": <str>,
                    "finished_ts": <str>,
                    "id": <int>,
                    "results": <str>,
                    "status": <str>,
                    "type": <str>
                  }
        """
        self._client._require_authentication("inventory.get_inventory_upload")
        self._validate_number("upload_id", upload_id, int, 1)
        return self._client._request(
            "GET", f"inventory/upload/{upload_id}"
        ).json()

from typing import TYPE_CHECKING, Any

from ..._shared import TTLCache, ResourceAPI, _copy_docstring
from .pages import PrivatePagesAPI
from .users import PrivateUsersAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivateMixesAPI(ResourceAPI):
    """
    Mixes API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateTIDALAPI"

    @TTLCache.cached_method(ttl="catalog")
    def get_mix_items(
        self, mix_id: str, /, country_code: str | None = None
    ) -> dict[str, Any]:
        """
        Get TIDAL catalog information for tracks in a mix.

        Parameters
        ----------
        mix_id : str; positional-only
            TIDAL ID of the mix.

            **Example**: :code:`"000ec0b01da1ddd752ec5dee553d48"`.

        country_code : str; optional
            ISO 3166-1 alpha-2 country code. If not provided, the
            country associated with the user account is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        items : dict[str, Any]
            TIDAL catalog information for tracks in the mix.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "items": [
                      {
                        "item": {
                          "accessType": <str>,
                          "adSupportedStreamReady": <bool>,
                          "album": {
                            "cover": <str>,
                            "id": <int>,
                            "title": <str>,
                            "vibrantColor": <str>,
                            "videoCover": <str>
                          },
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": <str>,
                            "id": <int>,
                            "name": <str>,
                            "picture": <str>,
                            "type": <str>
                          },
                          "artists": [
                            {
                              "handle": <str>,
                              "id": <int>,
                              "name": <str>,
                              "picture": <str>,
                              "type": <str>
                            }
                          ],
                          "audioModes": <list[str]>,
                          "audioQuality": <str>,
                          "bpm": <int>,
                          "copyright": <str>,
                          "djReady": <bool>,
                          "duration": <int>,
                          "editable": <bool>,
                          "explicit": <bool>,
                          "id": <int>,
                          "isrc": <str>,
                          "key": <str>,
                          "keyScale": <str>,
                          "mediaMetadata": {
                            "tags": <list[str]>
                          },
                          "mixes": {
                            "TRACK_MIX": <str>
                          },
                          "payToStream": <bool>,
                          "peak": <float>,
                          "popularity": <int>,
                          "premiumStreamingOnly": <bool>,
                          "replayGain": <float>,
                          "spotlighted": <bool>,
                          "stemReady": <bool>,
                          "streamReady": <bool>,
                          "streamStartDate": <str>,
                          "title": <str>,
                          "trackNumber": <int>,
                          "upload": <bool>,
                          "url": <str>,
                          "version": <str>,
                          "volumeNumber": <int>
                        },
                        "type": "track"
                      }
                    ],
                    "limit": <int>,
                    "offset": <int>,
                    "totalNumberOfItems": <int>
                  }
        """
        if country_code is None:
            country_code = self._client._my_country_code
        else:
            self._client._validate_country_code(country_code)
        return self._client._request(
            "GET",
            f"v1/mixes/{mix_id}/items",
            params={"countryCode": country_code},
        ).json()

    @_copy_docstring(PrivatePagesAPI.get_mix_page)
    def get_mix_page(
        self,
        mix_id: str,
        /,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
    ) -> dict[str, Any]:
        return self._client.pages.get_mix_page(
            mix_id, country_code, device_type=device_type, locale=locale
        )

    @_copy_docstring(PrivatePagesAPI.get_personalized_mixes_page)
    def get_personalized_mixes_page(
        self,
        country_code: str | None = None,
        *,
        device_type: str = "BROWSER",
        locale: str | None = None,
    ) -> dict[str, Any]:
        return self._client.pages.get_personalized_mixes_page(
            country_code, device_type=device_type, locale=locale
        )

    @_copy_docstring(PrivateUsersAPI.get_my_favorite_mixes)
    def get_my_favorite_mixes(
        self, *, limit: int = 50, cursor: str | None = None
    ) -> dict[str, Any]:
        return self._client.mixes.get_my_favorite_mixes(
            limit=limit, cursor=cursor
        )

    @_copy_docstring(PrivateUsersAPI.get_my_favorite_mix_ids)
    def get_my_favorite_mix_ids(
        self, *, limit: int = 50, cursor: str | None = None
    ) -> dict[str, Any]:
        return self._client.mixes.get_my_favorite_mix_ids(
            limit=limit, cursor=cursor
        )

    @_copy_docstring(PrivateUsersAPI.favorite_mixes)
    def favorite_mixes(
        self, mix_ids: str | list[str], /, *, missing_ok: bool | None = None
    ) -> None:
        return self._client.mixes.favorite_mixes(
            mix_ids, missing_ok=missing_ok
        )

    @_copy_docstring(PrivateUsersAPI.unfavorite_mixes)
    def unfavorite_mixes(self, mix_ids: str | list[str], /) -> None:
        return self._client.mixes.unfavorite_mixes(mix_ids)

    @staticmethod
    def _prepare_mix_ids(
        mix_ids: str | list[str], /, *, limit: int = 100
    ) -> str:
        """
        Stringify a list of TIDAL mix IDs into a comma-delimited string.

        Parameters
        ----------
        mix_ids : int, str, or list[str]; positional-only
            Comma-delimited string or list containing mix IDs.

        limit : int; keyword-only, default: :code:`100`
            Maximum number of mix IDs that can be sent in the request.

        Returns
        -------
        mix_ids : str
            Comma-delimited string containing mix IDs.
        """
        if not mix_ids:
            raise ValueError("At least one mix ID must be specified.")

        if isinstance(mix_ids, str):
            return PrivateMixesAPI._prepare_mix_ids(
                mix_ids.split(","), limit=limit
            )

        num_ids = len(mix_ids)
        if num_ids > limit:
            raise ValueError(
                f"A maximum of {limit} mix IDs can be sent in a request."
            )
        for id_ in mix_ids:
            if not isinstance(id_, str) or len(id_) != 30:
                raise ValueError(f"Invalid mix ID {id_!r}.")
        return ",".join(mix_ids)

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
                            "cover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                            "id": <int>,
                            "title": <str>,
                            "vibrantColor": "#rrggbb",
                            "videoCover": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx"
                          },
                          "allowStreaming": <bool>,
                          "artist": {
                            "handle": None,
                            "id": <int>,
                            "name": <str>,
                            "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
                            "type": <str>
                          },
                          "artists": [
                            {
                              "handle": None,
                              "id": <int>,
                              "name": <str>,
                              "picture": "xxxxxxxx-xxxx-4xxx-xxxx-xxxxxxxxxxxx",
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
                          "isrc": "CCXXXYYNNNNN",
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
                          "streamStartDate": "YYYY-MM-DDThh:mm:ss.sss±hhmm",
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

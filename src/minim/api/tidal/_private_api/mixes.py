from typing import Any

from ..._shared import TTLCache, _copy_docstring
from ._shared import PrivateTIDALResourceAPI
from .pages import PrivatePagesAPI
from .users import PrivateUsersAPI


class PrivateMixesAPI(PrivateTIDALResourceAPI):
    """
    Mixes API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="popularity")
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
            country associated with the current user account or IP
            address is used.

            **Example**: :code:`"US"`.

        Returns
        -------
        items : dict[str, Any]
            TIDAL content metadata for the tracks in the mix.

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
            self._validate_country_code(country_code)
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
            mix_id,
            country_code=country_code,
            device_type=device_type,
            locale=locale,
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
            country_code=country_code, device_type=device_type, locale=locale
        )

    @_copy_docstring(PrivateUsersAPI.get_my_followed_mixes)
    def get_my_followed_mixes(
        self, *, limit: int = 50, cursor: str | None = None
    ) -> dict[str, Any]:
        return self._client.mixes.get_my_followed_mixes(
            cursor=cursor, limit=limit
        )

    @_copy_docstring(PrivateUsersAPI.get_my_followed_mix_ids)
    def get_my_followed_mix_ids(
        self, *, limit: int = 50, cursor: str | None = None
    ) -> dict[str, Any]:
        return self._client.mixes.get_my_followed_mix_ids(
            cursor=cursor, limit=limit
        )

    @_copy_docstring(PrivateUsersAPI.follow_mixes)
    def follow_mixes(
        self, mix_ids: str | list[str], /, *, on_missing: str | None = None
    ) -> None:
        return self._client.mixes.follow_mixes(mix_ids, on_missing=on_missing)

    @_copy_docstring(PrivateUsersAPI.unfollow_mixes)
    def unfollow_mixes(self, mix_ids: str | list[str], /) -> None:
        return self._client.mixes.unfollow_mixes(mix_ids)

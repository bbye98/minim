from typing import Any

from ..._shared import TTLCache
from ._shared import PrivateTIDALResourceAPI


class PrivateFeedAPI(PrivateTIDALResourceAPI):
    """
    Feed API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPIClient`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="user")
    def get_feed_activities(self) -> dict[str, Any]:
        """
        Get feed activities for the current user.

        Returns
        -------
        feed_activities : dict[str, Any]
            Feed activities.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "activities": [
                      {
                        "followableActivity": {
                          "album": {
                            "id": <int>,
                            "title": <str>,
                            "artists": [
                              {
                                "id": <int>,
                                "name": <str>,
                              }
                            ],
                            "mainArtists": [
                              {
                                "id": <int>,
                                "name": <str>,
                              }
                            ],
                            "type": "ALBUM",
                            "audioQuality": <str>,
                            "streamStartDate": <str>,
                            "releaseDate": <str>,
                            "allowStreaming": <bool>,
                            "streamReady": <bool>,
                            "cover": <str>,
                            "videoCover": <str>,
                            "numberOfVolumes": <int>,
                            "numberOfTracks": <int>,
                            "numberOfVideos": <int>,
                            "explicit": <bool>
                          },
                          "activityType": "NEW_ALBUM_RELEASE",
                          "occurredAt": <str>
                        },
                        "seen": <bool>
                      }
                    ],
                    "stats": {
                      "totalNotSeenActivities": <int>
                    }
                  }
        """
        return self._client._request("GET", "v2/feed/activities").json()

    def mark_feed_activities_seen(self) -> None:
        """
        Mark all feed activities for the current user seen.
        """
        self._client._request("PUT", "v2/feed/activities/seen")

    @TTLCache.cached_method(ttl="user")
    def has_unseen_feed_activities(self) -> dict[str, bool]:
        """
        Check whether there are unseen feed activities for the current
        user.

        Returns
        -------
        unseen : dict[str, bool]
            Whether the current user has unseen feed activities.

            **Sample response**: :code:`{'hasUnseenActivities': False}`.
        """
        return self._client._request(
            "GET", "v2/feed/activities/unseen/exists"
        ).json()

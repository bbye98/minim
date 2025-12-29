from typing import TYPE_CHECKING, Any

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateTIDALAPI


class PrivateFeedAPI(ResourceAPI):
    """
    Feed API endpoints for the private TIDAL API.

    .. important::

       This class is managed by :class:`minim.api.tidal.PrivateTIDALAPI`
       and should not be instantiated directly.
    """

    _client: "PrivateTIDALAPI"

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

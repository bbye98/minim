from typing import Any

from ..._shared import TTLCache
from ._shared import MusixmatchResourceAPI


class MatcherAPI(MusixmatchResourceAPI):
    """
    Matcher API endpoints for the Musixmatch Lyrics API.

    .. important::

       This class is managed by
       :class:`minim.api.musixmatch.MusixmatchLyricsAPIClient` and
       should not be instantiated directly.
    """

    def match_track_lyrics(
        self, artist_query: str, track_query: str, *, isrc: str | None = None
    ) -> dict[str, Any]:
        """ """

    def match_track(
        self, artist_query: str, track_query: str, *, isrc: str | None = None
    ) -> dict[str, Any]:
        """ """

    def match_track_subtitles(
        self,
        artist_query: str,
        track_query: str,
        *,
        isrc: str | None = None,
        duration: int | str | None = None,
        max_duration_deviation: int | str | None = None,
    ) -> dict[str, Any]:
        """ """

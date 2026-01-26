from typing import Any

from ..._shared import _copy_docstring
from ._shared import MusixmatchResourceAPI
from .matcher import MatcherAPI
from .artists import ArtistsAPI
from .tracks import TracksAPI


class SearchAPI(MusixmatchResourceAPI):
    """
    Search-related endpoints for the Musixmatch Lyrics API.

    .. note::

       This class groups search-related endpoints for convenience.
       Musixmatch does not provide a dedicated Search API.

    .. important::

       This class is managed by
       :class:`minim.api.musixmatch.MusixmatchLyricsAPIClient` and
       should not be instantiated directly.
    """

    @_copy_docstring(MatcherAPI.match_track_lyrics)
    def match_track_lyrics(
        self,
        *,
        artist: str | None = None,
        track: str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        return self._client.matcher.match_track_lyrics(
            artist=artist, track=track, isrc=isrc
        )

    @_copy_docstring(MatcherAPI.match_track)
    def match_track(
        self,
        *,
        artist: str | None = None,
        track: str | None = None,
        isrc: str | None = None,
    ) -> dict[str, Any]:
        return self._client.matcher.match_track(
            artist=artist, track=track, isrc=isrc
        )

    @_copy_docstring(MatcherAPI.match_track_subtitles)
    def match_track_subtitles(
        self,
        *,
        artist: str | None = None,
        track: str | None = None,
        isrc: str | None = None,
        duration: int | str | None = None,
        max_duration_deviation: int | str | None = None,
    ) -> dict[str, Any]:
        return self._client.matcher.match_track_subtitles(
            artist=artist,
            track=track,
            isrc=isrc,
            duration=duration,
            max_duration_deviation=max_duration_deviation,
        )

    @_copy_docstring(ArtistsAPI.search_artists)
    def search_artists(
        self,
        artist_query: str | None = None,
        *,
        artist_id: int | str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        return self._client.artists.search_artists(
            artist_query=artist_query,
            artist_id=artist_id,
            limit=limit,
            page=page,
        )

    @_copy_docstring(TracksAPI.search_tracks)
    def search_tracks(
        self,
        query: str | None = None,
        *,
        artist_query: str | None = None,
        lyrics_query: str | None = None,
        track_query: str | None = None,
        track_artist_query: str | None = None,
        writer_query: str | None = None,
        artist_id: int | str | None = None,
        genre_id: int | str | None = None,
        language: str | None = None,
        has_lyrics: bool | None = None,
        release_date_after: str | None = None,
        release_date_before: str | None = None,
        artist_popularity_sort_order: str | None = None,
        track_popularity_sort_order: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._client.tracks.search_tracks(
            query=query,
            artist_query=artist_query,
            lyrics_query=lyrics_query,
            track_query=track_query,
            track_artist_query=track_artist_query,
            writer_query=writer_query,
            artist_id=artist_id,
            genre_id=genre_id,
            language=language,
            has_lyrics=has_lyrics,
            release_date_after=release_date_after,
            release_date_before=release_date_before,
            artist_popularity_sort_order=artist_popularity_sort_order,
            track_popularity_sort_order=track_popularity_sort_order,
            page=page,
            limit=limit,
        )

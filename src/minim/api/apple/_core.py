from collections.abc import Collection
from json.decoder import JSONDecodeError
import time
from typing import TYPE_CHECKING, Any
import warnings

from .._shared import APIClient

if TYPE_CHECKING:
    import httpx


class iTunesSearchAPI(APIClient):
    """
    iTunes Search API client.
    """

    _MEDIA_RELATIONSHIPS = {
        "all": {
            "entities": {
                "album",
                "allArtist",
                "allTrack",
                "audiobook",
                "mix",
                "movie",
                "musicVideo",
                "podcast",
                "tvSeason",
            },
            "attributes": {
                "actorTerm",
                "albumTerm",
                "allArtistTerm",
                "allTrackTerm",
                "artistTerm",
                "authorTerm",
                "composerTerm",
                "descriptionTerm",
                "directorTerm",
                "featureFilmTerm",
                "genreIndex",
                "keywordsTerm",
                "languageTerm",
                "mixTerm",
                "movieArtistTerm",
                "movieTerm",
                "producerTerm",
                "ratingIndex",
                "ratingTerm",
                "releaseYearTerm",
                "shortFilmTerm",
                "showTerm",
                "songTerm",
                "titleTerm",
                "tvEpisodeTerm",
                "tvSeasonTerm",
            },
        },
        "audiobook": {
            "entities": {"audiobook", "audiobookAuthor"},
            "attributes": {
                "authorTerm",
                "genreIndex",
                "ratingIndex",
                "titleTerm",
            },
        },
        "ebook": {"entities": {"ebook"}, "attributes": {}},
        "movie": {
            "entities": {"movie", "movieArtist"},
            "attributes": {
                "actorTerm",
                "artistTerm",
                "descriptionTerm",
                "directorTerm",
                "featureFilmTerm",
                "genreIndex",
                "movieArtistTerm",
                "movieTerm",
                "producerTerm",
                "ratingIndex",
                "ratingTerm",
                "releaseYearTerm",
                "shortFilmTerm",
            },
        },
        "music": {
            "entities": {
                "album",
                "mix",
                "musicArtist",
                "musicTrack",
                "musicVideo",
                "song",
            },
            "attributes": {
                "albumTerm",
                "artistTerm",
                "composerTerm",
                "genreIndex",
                "mixTerm",
                "ratingIndex",
                "songTerm",
            },
        },
        "musicVideo": {
            "entities": {"musicArtist", "musicVideo"},
            "attributes": {
                "albumTerm",
                "artistTerm",
                "genreIndex",
                "ratingIndex",
                "songTerm",
            },
        },
        "podcast": {
            "entities": {"podcast", "podcastAuthor", "podcastEpisode"},
            "attributes": {
                "artistTerm",
                "authorTerm",
                "descriptionTerm",
                "genreIndex",
                "keywordsTerm",
                "languageTerm",
                "ratingIndex",
                "titleTerm",
            },
        },
        "shortFilm": {
            "entities": {"shortFilm", "shortFilmArtist"},
            "attributes": {
                "artistTerm",
                "descriptionTerm",
                "genreIndex",
                "ratingIndex",
                "shortFilmTerm",
            },
        },
        "software": {
            "entities": {"desktopSoftware", "iPadSoftware", "software"},
            "attributes": {"softwareDeveloper"},
        },
        "tvShow": {
            "entities": {"tvEpisode", "tvSeason"},
            "attributes": {
                "descriptionTerm",
                "genreIndex",
                "ratingIndex",
                "showTerm",
                "tvEpisodeTerm",
                "tvSeasonTerm",
            },
        },
    }
    _PROVIDER: str = "Apple"
    _QUAL_NAME: str = "minim.api.apple.iTunesSearchAPI"
    BASE_URL: str = "https://itunes.apple.com"

    def lookup(
        self,
        *,
        itunes_id: int | str | Collection[int | str] | None = None,
        amg_album_id: int | str | Collection[int | str] | None = None,
        amg_artist_id: int | str | Collection[int | str] | None = None,
        amg_video_id: int | str | Collection[int | str] | None = None,
        bundle_id: str | Collection[str] | None = None,
        isbns: int | str | Collection[int | str] | None = None,
        upcs: int | str | Collection[int | str] | None = None,
        entity: str | None = None,
        limit: int | str | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        """ """
        pass

    def search(
        self,
        term: str,
        /,
        country: str,
        *,
        medium: str | None = None,
        entity: str | None = None,
        limit: int | None = None,
        lang: int | None = None,
        version: int | None = None,
        explicit: bool | None = None,
    ) -> dict[str, Any]:
        """ """
        self._validate_type("term", term, str)
        self._validate_locale(country)
        params = {"term": term, "country": country}
        return self._request("GET", "search", params=params)

    def _request(
        self,
        method: str,
        endpoint: str,
        /,
        retry: bool = True,
        **kwargs: dict[str, Any],
    ) -> "httpx.Response":
        """
        Make an HTTP request to a iTunes Search API endpoint.

        Parameters
        ----------
        method : str, positional-only
            HTTP method.

        endpoint : str, positional-only
            iTunes Search API endpoint.

        retry : bool, keyword-only, default: :code:`True`
            Whether to retry the request if the first attempt returns a
            :code:`403 Forbidden`.

        **kwargs : dict[str, Any]
            Keyword arguments to pass to :meth:`httpx.Client.request`.

        Returns
        -------
        response : httpx.Response
            HTTP response.
        """
        resp = self._client.request(method, endpoint, **kwargs)
        status = resp.status_code
        if 200 <= status < 300:
            return resp

        if status == 403 and retry:
            retry_after = 0.3333333333333333
            warnings.warn(
                f"Rate limit exceeded. Retrying after {retry_after:.3f} second(s)."
            )
            time.sleep(retry_after)
            return self._request(method, endpoint, retry=False, **kwargs)
        emsg = f"{status} {resp.reason_phrase}"
        try:
            if details := resp.json()["errorMessage"]:
                emsg += f" – {details}"
        except JSONDecodeError:
            pass
        raise RuntimeError(emsg)

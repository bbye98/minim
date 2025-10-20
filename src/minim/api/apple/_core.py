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

    .. seealso::

       For more information, see the `iTunes Search API
       documentation <https://developer.apple.com/library/archive
       /documentation/AudioVideo/Conceptual/iTuneSearchAPI
       /index.html>`_.
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
        """
        Search for content using iTunes IDs, All Music Guide (AMG) IDs,
        Universal Product Codes (UPCs), European Article Numbers (EANs),
        or International Standard Book Numbers (ISBNs).
        """
        pass

    def search(
        self,
        term: str,
        /,
        country: str,
        *,
        media: str | None = None,
        entity: str | None = None,
        attribute: str | None = None,
        limit: int | None = None,
        lang: int | None = None,
        version: int | None = None,
        explicit: bool | str | None = None,
    ) -> dict[str, Any]:
        """
        Search for content using a text string.

        Parameters
        ----------
        term : str, positional-only
            Text to search for.

            **Example**: :code:`"jack johnson"`.

        country : str
            ISO 3166-1 alpha-2 country code.

            **Default**: :code:`"US"`.

        media : str, keyword-only, optional
            Media type to search for.

            **Valid values**: :code:`"all"`, :code:`"audiobook"`,
            :code:`"ebook"`, :code:`"movie"`, :code:`"music"`,
            :code:`"musicVideo"`, :code:`"podcast"`,
            :code:`"shortFilm"`, :code:`"software"`, :code:`"tvShow"`.

            **Default**: :code:`"all"`.

        entity : str, keyword-only, optional
            ...

        attribute : str, keyword-only, optional
            ...

        limit : int, keyword-only, optional
            ...

        lang : int, keyword-only, optional
            ...

        version : int, keyword-only, optional
            ...

        explicit : bool | str, keyword-only, optional
            ...

        Returns
        -------
        results : dict[str, Any]
            Search results.

            .. admonition:: Sample response
               :class: dropdown

               ...
        """
        self._validate_type("term", term, str)
        self._validate_locale(country)
        params = {"term": term, "country": country}
        if media is None:
            emsg_suffix = ""
        else:
            self._validate_type("media", media, str)
            if media not in self._MEDIA_RELATIONSHIPS:
                _media = "', '".join(self._MEDIA_RELATIONSHIPS)
                raise ValueError(
                    f"Invalid media type {media!r}. Valid values: '{_media}'."
                )
            params["media"] = media
            emsg_suffix = f" for media type '{media}'"
        if entity is not None:
            self._validate_type("entity", entity, str)
            entities = self._MEDIA_RELATIONSHIPS[media or "all"]["entities"]
            if entity not in entities:
                entities = "', '".join(entities)
                raise ValueError(
                    f"Invalid entity {entity!r}{emsg_suffix}. "
                    f"Valid values: '{entities}'."
                )
        if attribute is not None:
            self._validate_type("attribute", attribute, str)
            attributes = self._MEDIA_RELATIONSHIPS[media or "all"]["attributes"]
            if attribute not in attributes:
                attributes = "', '".join(attributes)
                raise ValueError(
                    f"Invalid attribute {attribute!r}{emsg_suffix}. "
                    f"Valid values: '{attributes}'."
                )
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 200)
            params["limit"] = limit
        if lang is not None:
            self._validate_locale(lang)
            params["lang"] = lang
        if version is not None:
            self._validate_number("version", version, int, 1, 2)
            params["version"] = version
        if explicit is not None:
            self._validate_type("explicit", explicit, bool | str)
            if isinstance(explicit, bool):
                params["explicit"] = "Yes" if explicit else "No"
            elif explicit in {"Yes", "No"}:
                params["explicit"] = explicit
            else:
                raise ValueError("`explicit` must be 'Yes'/True or 'No'/False.")
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

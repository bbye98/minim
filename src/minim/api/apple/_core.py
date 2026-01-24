from json.decoder import JSONDecodeError
import time
from typing import TYPE_CHECKING, Any
import warnings

from .._shared import TTLCache, APIClient, ResourceAPI

if TYPE_CHECKING:
    import httpx


class iTunesSearchAPIClient(APIClient):
    """
    iTunes Search API client.
    """

    _MEDIA_TYPES = {
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
    _PROVIDER = "Apple"
    _QUAL_NAME = f"minim.api.{_PROVIDER.lower()}.{__qualname__}"
    _RATE_LIMIT_PER_SECOND = 1 / 3
    BASE_URL = "https://itunes.apple.com"

    def _request(
        self,
        method: str,
        endpoint: str,
        /,
        retry: bool = True,
        **kwargs: dict[str, Any],
    ) -> "httpx.Response":
        """
        Make an HTTP request to an iTunes Search API endpoint.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

        endpoint : str; positional-only
            iTunes Search API endpoint.

        retry : bool; keyword-only; default: :code:`True`
            Whether to retry the request if it returns
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
            retry_after = self._RATE_LIMIT_PER_SECOND
            warnings.warn(
                "Rate limit possibly exceeded. Retrying after "
                f"{retry_after:.3f} second(s)."
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

    @TTLCache.cached_method(ttl="static")
    def lookup(
        self,
        *,
        itunes_ids: int | str | list[int | str] | None = None,
        amg_album_ids: int | str | list[int | str] | None = None,
        amg_artist_ids: int | str | list[int | str] | None = None,
        amg_video_ids: int | str | list[int | str] | None = None,
        bundle_ids: str | list[str] | None = None,
        isbns: int | str | list[int | str] | None = None,
        barcodes: int | str | list[int | str] | None = None,
        item_type: str | None = None,
        limit: int | str | None = None,
        order: str | None = None,
    ) -> dict[str, Any]:
        """
        Get Apple catalog information for albums, artists, audiobooks,
        ebooks, movies, music, music videos, podcasts, and television
        shows using their iTunes IDs, All Music Guide (AMG) IDs,
        Universal Product Codes (UPCs), European Article Numbers (EANs),
        or International Standard Book Numbers (ISBNs).

        .. important::

           Exactly one of `itunes_ids`, `amg_album_ids`,
           `amg_artist_ids`, `amg_video_ids`, `bundle_ids`, `isbns`,
           or `barcodes` must be provided.

        Parameters
        ----------
        itunes_ids : int, str, or list[int | str]; keyword-only; \
        optional
            iTunes IDs.

            **Examples**: :code:`984746615`, :code:`"1440935756"`,
            :code:`[984746615, "1440935756"]`.

        amg_album_ids : int, str, or list[int | str]; keyword-only; \
        optional
            AMG album IDs.

            **Examples**: :code:`2025410`, :code:`"2844399"`,
            :code:`[2025410, "2844399"]`.

        amg_artist_ids : int, str, or list[int | str]; keyword-only; \
        optional
            AMG artist IDs.

            **Examples**: :code:`472102`, :code:`"2913530"`,
            :code:`[472102, "2913530"]`.

        amg_video_ids : int, str, or list[int | str]; keyword-only; \
        optional
            AMG video IDs.

            **Examples**: :code:`17120`, :code:`"17121"`,
            :code:`[17122, "17123"]`.

        bundle_ids : str or list[str]; keyword-only; optional
            App bundle IDs.

            **Examples**: :code:`"com.tripadvisor.LocalPicks"`,
            :code:`["com.tripadvisor.LocalPicks",
            "com.yelp.yelpiphone"]`.

        isbns : int, str, or list[int | str]; keyword-only; optional
            ISBNs.

            **Examples**: :code:`9781637993415`,
            :code:`"9781705142110"`,
            :code:`[9781637993415, "9781705142110"]`.

        barcodes : int, str, or list[int | str]; keyword-only; optional
            Barcodes (UPCs and/or EANs).

            **Examples**: :code:`602448438034`, :code:`"075678671173"`,
            :code:`[602448438034, "075678671173"]`.

        item_type : str; keyword-only; optional
            Type of item to return.

            .. seealso::

               `Table 2-1 in the iTunes Search API Documentation
               (Archived) <https://developer.apple.com/library/archive
               /documentation/AudioVideo/Conceptual/iTuneSearchAPI
               /Searching.html#//apple_ref/doc/uid
               /TP40017632-CH5-SW2>`__ – Available item (or entity)
               types.

            **Example**: :code:`"movieArtist"`.

        limit : int; keyword-only; optional
            Maximum number of results to return.

            **Valid range**: :code:`1` to :code:`200`.

            **API default**: :code:`50`.

        order : str; keyword-only; optional
            Ordering mode for the results.

            **Valid value**: :code:`"recent"`.

        Returns
        -------
        results : dict[str, Any]
            Lookup results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                     {
                       "resultCount": <int>,
                       "results": [
                         {
                           "amgArtistId": <int>,
                           "artistId": <int>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl60": <str>,
                           "collectionCensoredName": <str>,
                           "collectionExplicitness": <str>,
                           "collectionId": <int>,
                           "collectionName": <str>,
                           "collectionType": <str>,
                           "collectionViewUrl": <str>,
                           "contentAdvisoryRating": <str>,
                           "copyright": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "trackCount": <int>,
                           "wrapperType": "collection"
                         },
                         {
                           "amgArtistId": <int>,
                           "artistId": <int>,
                           "artistLinkUrl": <str>,
                           "artistName": <str>,
                           "artistType": <str>,
                           "primaryGenreId": <int>,
                           "primaryGenreName": <str>,
                           "wrapperType": "artist"
                         },
                         {
                           "amgArtistId": <int>,
                           "artistId": <int>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl60": <str>,
                           "collectionCensoredName": <str>,
                           "collectionExplicitness": <str>,
                           "collectionId": <int>,
                           "collectionName": <str>,
                           "collectionPrice": <float>,
                           "collectionViewUrl": <str>,
                           "copyright": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "description": <str>,
                           "previewUrl": <str>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "trackCount": <int>,
                           "wrapperType": "audiobook"
                         },
                         {
                           "artistId": <int>,
                           "artistIds": <list[int]>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl60": <str>,
                           "averageUserRating": <float>,
                           "currency": <str>,
                           "description": <str>,
                           "formattedPrice": <str>,
                           "genreIds": <list[str]>,
                           "genres": <list[str]>,
                           "kind": "ebook",
                           "price": <float>,
                           "releaseDate": <str>,
                           "trackCensoredName": <str>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackViewUrl": <str>,
                           "userRatingCount": <int>
                         },
                         {
                           "artistName": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl30": <str>,
                           "artworkUrl60": <str>,
                           "artworkUrl600": <str>,
                           "collectionCensoredName": <str>,
                           "collectionExplicitness": <str>,
                           "collectionHdPrice": <int>,
                           "collectionId": <int>,
                           "collectionName": <str>,
                           "collectionPrice": <float>,
                           "collectionViewUrl": <str>,
                           "contentAdvisoryRating": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "feedUrl": <str>,
                           "genreIds": <list[str]>,
                           "genres": <list[str]>,
                           "kind": "podcast",
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "trackCensoredName": <str>,
                           "trackCount": <int>,
                           "trackExplicitness": <str>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackPrice": <float>,
                           "trackTimeMillis": <int>,
                           "trackViewUrl": <str>,
                           "wrapperType": "track"
                         }
                         {
                           "artistId": <int>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl30": <str>,
                           "artworkUrl60": <str>,
                           "collectionArtistId": <int>,
                           "collectionArtistName": <str>,
                           "collectionCensoredName": <str>,
                           "collectionExplicitness": <str>,
                           "collectionId": <int>,
                           "collectionName": <str>,
                           "collectionPrice": <float>,
                           "collectionViewUrl": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "discCount": <int>,
                           "discNumber": <int>,
                           "isStreamable": <bool>,
                           "kind": <str>,
                           "previewUrl": <str>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "trackCensoredName": <str>,
                           "trackCount": <int>,
                           "trackExplicitness": <str>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackNumber": <int>,
                           "trackPrice": <float>,
                           "trackTimeMillis": <int>,
                           "trackViewUrl": <str>,
                           "wrapperType": "track"
                         },
                         {
                           "artistId": <int>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl30": <str>,
                           "artworkUrl60": <str>,
                           "collectionCensoredName": <str>,
                           "collectionExplicitness": <str>,
                           "collectionHdPrice": <float>,
                           "collectionId": <int>,
                           "collectionName": <str>,
                           "collectionPrice": <float>,
                           "collectionViewUrl": <str>,
                           "contentAdvisoryRating": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "discCount": <int>,
                           "discNumber": <int>,
                           "kind": "tv-episode",
                           "longDescription": <str>,
                           "previewUrl": <str>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "shortDescription": <str>,
                           "trackCensoredName": <str>,
                           "trackCount": <int>,
                           "trackExplicitness": <str>,
                           "trackHdPrice": <float>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackNumber": <int>,
                           "trackPrice": <float>,
                           "trackTimeMillis": <int>,
                           "trackViewUrl": <str>,
                           "wrapperType": "track"
                         },
                         {
                           "advisories": <list[str]>,
                           "appletvScreenshotUrls": <list[str]>,
                           "artistId": <int>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl512": <str>,
                           "artworkUrl60": <str>,
                           "averageUserRating": <float>,
                           "averageUserRatingForCurrentVersion": <float>,
                           "bundleId": <str>,
                           "contentAdvisoryRating": <str>,
                           "currency": <str>,
                           "currentVersionReleaseDate": <str>,
                           "description": <str>,
                           "features": <list[str]>,
                           "fileSizeBytes": <str>,
                           "formattedPrice": <str>,
                           "genreIds": <list[str]>,
                           "genres": <list[str]>,
                           "ipadScreenshotUrls": <list[str]>,
                           "isGameCenterEnabled": <bool>,
                           "isVppDeviceBasedLicensingEnabled": <bool>,
                           "kind": "software",
                           "languageCodesISO2A": <list[str]>,
                           "minimumOsVersion": <str>,
                           "price": <float>,
                           "primaryGenreId": <int>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "releaseNotes": <str>,
                           "screenshotUrls": <list[str]>,
                           "sellerName": <str>,
                           "sellerUrl": <str>,
                           "supportedDevices": <list[str]>,
                           "trackCensoredName": <str>,
                           "trackContentRating": <str>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackViewUrl": <str>,
                           "userRatingCount": <int>,
                           "userRatingCountForCurrentVersion": <int>,
                           "version": <str>,
                           "wrapperType": "software"
                         }
                       ]
                     }
        """
        emsg = (
            "Exactly one of `itunes_ids`, `amg_album_ids`, "
            "`amg_artist_ids`, `amg_video_ids`, `bundle_ids`, `isbns`, "
            "or `barcodes` must be provided."
        )
        params = {}
        _locals = locals()
        for arg_name, param_name, is_int_like in [
            ("itunes_ids", "id", True),
            ("amg_album_ids", "amgAlbumId", True),
            ("amg_artist_ids", "amgArtistId", True),
            ("amg_video_ids", "amgVideoId", True),
            ("bundle_ids", "bundleId", False),
            ("isbns", "isbn", True),
            ("barcodes", "upc", True),
        ]:
            if (arg := _locals.get(arg_name)) is not None:
                if len(params):
                    raise ValueError(emsg)
                if not isinstance(arg, list | tuple):
                    arg = [arg]
                if is_int_like:
                    _validate = ResourceAPI._validate_numeric
                    dtype = int
                else:
                    _validate = ResourceAPI._validate_type
                    dtype = str
                for idx, val in enumerate(arg):
                    _validate(f"{arg_name}[{idx}]", val, dtype)
                params[param_name] = ",".join(str(val) for val in arg)
        if not len(params):
            raise ValueError(emsg)

        if item_type is not None:
            if item_type not in (
                entities := self._MEDIA_TYPES["all"]["entities"]
            ):
                entities_str = "', '".join(sorted(entities))
                raise ValueError(
                    f"Invalid item type {item_type!r}. "
                    f"Valid values: '{entities_str}'."
                )
        if limit is not None:
            ResourceAPI._validate_number("limit", limit, int, 1, 200)
            params["limit"] = limit
        if order is not None:
            if order.lower() != "recent":
                raise ValueError(
                    f"Invalid ordering mode {order!r}. Valid value: 'recent'."
                )
            params["sort"] = order
        return self._request("GET", "lookup", params=params).json()

    @TTLCache.cached_method(ttl="search")
    def search(
        self,
        query: str,
        /,
        country_code: str,
        *,
        media_type: str | None = None,
        item_type: str | None = None,
        search_field: str | None = None,
        limit: int | None = None,
        locale: str | None = None,
        api_version: int | None = None,
        include_explicit: bool | str | None = None,
    ) -> dict[str, Any]:
        """
        Search for audiobooks, ebooks, movies, music, music videos,
        podcasts, and/or television shows in the Apple catalog.

        Parameters
        ----------
        query : str; positional-only
            Search query.

            **Example**: :code:`"jack johnson"`.

        country : str
            ISO 3166-1 alpha-2 country code.

        media_type : str; keyword-only; optional
            Media type to search for.

            **Valid values**: :code:`"all"`, :code:`"audiobook"`,
            :code:`"ebook"`, :code:`"movie"`, :code:`"music"`,
            :code:`"musicVideo"`, :code:`"podcast"`,
            :code:`"shortFilm"`, :code:`"software"`, :code:`"tvShow"`.

            **API default**: :code:`"all"`.

        item_type : str; keyword-only; optional
            Type of item to return for the given media type.

            .. seealso::

               `Table 2-1 in the iTunes Search API Documentation
               (Archived) <https://developer.apple.com/library/archive
               /documentation/AudioVideo/Conceptual/iTuneSearchAPI
               /Searching.html#//apple_ref/doc/uid
               /TP40017632-CH5-SW2>`__ – Available item (or entity)
               types for each media type.

            **Example**: :code:`"movieArtist"` when
            :code:`media="movie"`.

            **API default**: Track item type associated with the
            media type.

        search_field : str; keyword-only; optional
            Field to search within for the given media type.

            .. seealso::

               `iTunes Search API Documentation (Apple Services
               Performance Partner Program)
               <https://performance-partners.apple.com/search-api>`__ –
               Available search fields (or attributes) for each media
               type.

            **Example**: :code:`"allArtistTerm"` when
            :code:`media="all"` and :code:`entity="allArtist"`.

        limit : int; keyword-only; optional
            Maximum number of results to return.

            **Valid range**: :code:`1` to :code:`200`.

            **API default**: :code:`50`.

        locale : str; keyword-only; optional
            IETF BCP 47 language tag consisting of an ISO 639-1 language
            code and an ISO 3166-1 alpha-2 country code joined by an
            underscore. If provided, results are returned in the
            specified language.

            **Valid values**:

            .. container::

               * :code:`"en_us"` – English.
               * :code:`"ja_jp"` – Japanese.

            **API default**: :code:`"en_us"`.

        api_version : int; keyword-only; optional
            Search result key version.

            **Valid values**: :code:`1`, :code:`2`.

            **API default**: :code:`2`.

        include_explicit : bool or str; keyword-only; optional
            Whether to include explicit content in the results.

            **Valid values**: :code:`"Yes"` (or :code:`True`),
            :code:`"No"` (or :code:`False`).

            **API default**: :code:`"Yes"`.

        Returns
        -------
        results : dict[str, Any]
            Search results.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: Current (:code:`v2`) response

                  .. code::

                     {
                       "resultCount": <int>,
                       "results": [
                         {
                           "amgArtistId": <int>,
                           "artistId": <int>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl60": <str>,
                           "collectionCensoredName": <str>,
                           "collectionExplicitness": <str>,
                           "collectionId": <int>,
                           "collectionName": <str>,
                           "collectionPrice": <float>,
                           "collectionViewUrl": <str>,
                           "copyright": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "description": <str>,
                           "previewUrl": <str>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "trackCount": <int>,
                           "wrapperType": "audiobook"
                         },
                         {
                           "artistId": <int>,
                           "artistIds": <list[int]>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl60": <str>,
                           "averageUserRating": <float>,
                           "currency": <str>,
                           "description": <str>,
                           "formattedPrice": <str>,
                           "genreIds": <list[str]>,
                           "genres": <list[str]>,
                           "kind": "ebook",
                           "price": <float>,
                           "releaseDate": <str>,
                           "trackCensoredName": <str>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackViewUrl": <str>,
                           "userRatingCount": <int>
                         },
                         {
                           "artistName": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl30": <str>,
                           "artworkUrl60": <str>,
                           "artworkUrl600": <str>,
                           "collectionCensoredName": <str>,
                           "collectionExplicitness": <str>,
                           "collectionHdPrice": <int>,
                           "collectionId": <int>,
                           "collectionName": <str>,
                           "collectionPrice": <float>,
                           "collectionViewUrl": <str>,
                           "contentAdvisoryRating": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "feedUrl": <str>,
                           "genreIds": <list[str]>,
                           "genres": <list[str]>,
                           "kind": "podcast",
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "trackCensoredName": <str>,
                           "trackCount": <int>,
                           "trackExplicitness": <str>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackPrice": <float>,
                           "trackTimeMillis": <int>,
                           "trackViewUrl": <str>,
                           "wrapperType": "track"
                         }
                         {
                           "artistId": <int>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl30": <str>,
                           "artworkUrl60": <str>,
                           "collectionArtistId": <int>,
                           "collectionArtistName": <str>,
                           "collectionCensoredName": <str>,
                           "collectionExplicitness": <str>,
                           "collectionId": <int>,
                           "collectionName": <str>,
                           "collectionPrice": <float>,
                           "collectionViewUrl": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "discCount": <int>,
                           "discNumber": <int>,
                           "isStreamable": <bool>,
                           "kind": <str>,
                           "previewUrl": <str>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "trackCensoredName": <str>,
                           "trackCount": <int>,
                           "trackExplicitness": <str>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackNumber": <int>,
                           "trackPrice": <float>,
                           "trackTimeMillis": <int>,
                           "trackViewUrl": <str>,
                           "wrapperType": "track"
                         },
                         {
                           "artistId": <int>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl30": <str>,
                           "artworkUrl60": <str>,
                           "collectionCensoredName": <str>,
                           "collectionExplicitness": <str>,
                           "collectionHdPrice": <float>,
                           "collectionId": <int>,
                           "collectionName": <str>,
                           "collectionPrice": <float>,
                           "collectionViewUrl": <str>,
                           "contentAdvisoryRating": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "discCount": <int>,
                           "discNumber": <int>,
                           "kind": "tv-episode",
                           "longDescription": <str>,
                           "previewUrl": <str>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "shortDescription": <str>,
                           "trackCensoredName": <str>,
                           "trackCount": <int>,
                           "trackExplicitness": <str>,
                           "trackHdPrice": <float>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackNumber": <int>,
                           "trackPrice": <float>,
                           "trackTimeMillis": <int>,
                           "trackViewUrl": <str>,
                           "wrapperType": "track"
                         },
                         {
                           "advisories": <list[str]>,
                           "appletvScreenshotUrls": <list[str]>,
                           "artistId": <int>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl512": <str>,
                           "artworkUrl60": <str>,
                           "averageUserRating": <float>,
                           "averageUserRatingForCurrentVersion": <float>,
                           "bundleId": <str>,
                           "contentAdvisoryRating": <str>,
                           "currency": <str>,
                           "currentVersionReleaseDate": <str>,
                           "description": <str>,
                           "features": <list[str]>,
                           "fileSizeBytes": <str>,
                           "formattedPrice": <str>,
                           "genreIds": <list[str]>,
                           "genres": <list[str]>,
                           "ipadScreenshotUrls": <list[str]>,
                           "isGameCenterEnabled": <bool>,
                           "isVppDeviceBasedLicensingEnabled": <bool>,
                           "kind": "software",
                           "languageCodesISO2A": <list[str]>,
                           "minimumOsVersion": <str>,
                           "price": <float>,
                           "primaryGenreId": <int>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "releaseNotes": <str>,
                           "screenshotUrls": <list[str]>,
                           "sellerName": <str>,
                           "sellerUrl": <str>,
                           "supportedDevices": <list[str]>,
                           "trackCensoredName": <str>,
                           "trackContentRating": <str>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackViewUrl": <str>,
                           "userRatingCount": <int>,
                           "userRatingCountForCurrentVersion": <int>,
                           "version": <str>,
                           "wrapperType": "software"
                         }
                       ]
                     }

               .. tab:: Legacy (:code:`v1`) response

                  .. code::

                     {
                       "resultCount": <int>,
                       "results": [
                         {
                           "amgArtistId": <int>,
                           "artistId": <int>,
                           "artistName": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl60": <str>,
                           "collectionId": <int>,
                           "copyright": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "itemExplicitness": <str>,
                           "itemId": <int>,
                           "itemLinkUrl": <str>,
                           "itemPrice": <str>,
                           "primaryGenreId": <int>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "wrapperType": "audiobook"
                         },
                         {
                           "artistLinkUrl": <str>,
                           "artistName": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl60": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "discCount": <int>,
                           "discNumber": <int>,
                           "itemCensoredName": <str>,
                           "itemExplicitness": <str>,
                           "itemLinkUrl": <str>,
                           "itemName": <str>,
                           "itemParentCensoredName": <str>,
                           "itemParentExplicitness": <str>,
                           "itemParentLinkUrl": <str>,
                           "itemParentName": <str>,
                           "itemParentPrice": <str>,
                           "itemPrice": <str>,
                           "kind": <str>,
                           "mediaType": <str>,
                           "previewUrl": <str>,
                           "primaryGenreName": <str>,
                           "trackCount": <int>,
                           "trackNumber": <int>,
                           "trackTime": <int>,
                           "wrapperType": "track"
                         },
                       ]
                     }
        """
        ResourceAPI._validate_type("query", query, str)
        query = query.strip()
        if not len(query):
            raise ValueError("No search query provided.")
        ResourceAPI._validate_country_code(country_code)
        params = {"term": query, "country": country_code}
        if media_type is None:
            emsg_suffix = ""
        else:
            if media_type not in self._MEDIA_TYPES:
                media_types_str = "', '".join(sorted(self._MEDIA_TYPES))
                raise ValueError(
                    f"Invalid media type {media_type!r}. "
                    f"Valid values: '{media_types_str}'."
                )
            params["media"] = media_type
            emsg_suffix = f" for media type {media_type!r}"
        if item_type is not None:
            if item_type not in (
                entities := self._MEDIA_TYPES[media_type or "all"]["entities"]
            ):
                entities_str = "', '".join(sorted(entities))
                raise ValueError(
                    f"Invalid item type {item_type!r}{emsg_suffix}."
                    f"Valid values: '{entities_str}'."
                )
        if search_field is not None:
            if search_field not in (
                attributes := self._MEDIA_TYPES[media_type or "all"][
                    "attributes"
                ]
            ):
                attributes_str = "', '".join(sorted(attributes))
                raise ValueError(
                    f"Invalid search field {search_field!r}{emsg_suffix}. "
                    f"Valid values: '{attributes_str}'."
                )
        if limit is not None:
            ResourceAPI._validate_number("limit", limit, int, 1, 200)
            params["limit"] = limit
        if locale is not None:
            ResourceAPI._validate_locale(locale)
            if locale.lower() not in {"en_us", "ja_jp"}:
                raise ValueError(
                    f"Invalid language tag {locale!r}. "
                    "Valid values: 'en_us', 'ja_jp'."
                )
            params["lang"] = locale
        if api_version is not None:
            ResourceAPI._validate_number("api_version", api_version, int, 1, 2)
            params["version"] = api_version
        if include_explicit is not None:
            ResourceAPI._validate_type(
                "include_explicit", include_explicit, bool | str
            )
            if isinstance(include_explicit, bool):
                params["explicit"] = "Yes" if include_explicit else "No"
            elif include_explicit.lower() in {"yes", "no"}:
                params["explicit"] = include_explicit
            else:
                raise ValueError(
                    "`include_explicit` can only be 'Yes'/True or 'No'/False."
                )
        return self._request("GET", "search", params=params).json()

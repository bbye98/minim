from collections.abc import Collection
from json.decoder import JSONDecodeError
import time
from typing import TYPE_CHECKING, Any
import warnings

from .._shared import TTLCache, APIClient

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
    _RATE_LIMIT_PER_SECOND = 1 / 3
    BASE_URL: str = "https://itunes.apple.com"

    @TTLCache.cached_method(ttl="catalog")
    def lookup(
        self,
        *,
        itunes_ids: int | str | Collection[int | str] | None = None,
        amg_album_ids: int | str | Collection[int | str] | None = None,
        amg_artist_ids: int | str | Collection[int | str] | None = None,
        amg_video_ids: int | str | Collection[int | str] | None = None,
        bundle_ids: str | Collection[str] | None = None,
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

        Parameters
        ----------
        itunes_ids : int, str, or Collection[int | str], keyword-only, \
        optional
            iTunes IDs to look up.

            .. note::

               Exactly one of `itunes_ids`, `amg_album_ids`,
               `amg_artist_ids`, `amg_video_ids`, `bundle_ids`, `isbns`,
               or `upcs` must be provided.

            **Examples**: :code:`1690873457`, :code:`"984746615"`,
            :code:`[1690873457, 984746615]`,
            :code:`["1690873457", "984746615"]`.

        amg_album_ids : int, str, or Collection[int | str], \
        keyword-only, optional
            AMG album IDs to look up.

            .. note::

               Exactly one of `itunes_ids`, `amg_album_ids`,
               `amg_artist_ids`, `amg_video_ids`, `bundle_ids`, `isbns`,
               or `upcs` must be provided.

            **Examples**: :code:`15175`, :code:`15176`,
            :code:`[15177, 15178]`, :code:`["15183", "15184"]`.

        amg_artist_ids : int, str, or Collection[int | str], \
        keyword-only, optional
            AMG artist IDs to look up.

            .. note::

               Exactly one of `itunes_ids`, `amg_album_ids`,
               `amg_artist_ids`, `amg_video_ids`, `bundle_ids`, `isbns`,
               or `upcs` must be provided.

            **Examples**: :code:`816977`, :code:`"2342870"`,
            :code:`[816977, 2342870]`, :code:`["816977", "2342870"]`.

        amg_video_ids : int, str, or Collection[int | str], \
        keyword-only, optional
            AMG video IDs to look up.

            .. note::

               Exactly one of `itunes_ids`, `amg_album_ids`,
               `amg_artist_ids`, `amg_video_ids`, `bundle_ids`, `isbns`,
               or `upcs` must be provided.

            **Examples**: :code:`17120`, :code:`"17121"`,
            :code:`[17122, 17123]`, :code:`["17124", "17125"]`.

        bundle_ids : str, or Collection[str], keyword-only, optional
            App bundle IDs to look up.

            .. note::

               Exactly one of `itunes_ids`, `amg_album_ids`,
               `amg_artist_ids`, `amg_video_ids`, `bundle_ids`, `isbns`,
               or `upcs` must be provided.

            **Examples**: :code:`"com.yelp.yelpiphone"`,
            :code:`["com.tripadvisor.LocalPicks", "com.yelp.yelpiphone"]`.

        isbns : int, str, or Collection[int | str], keyword-only, \
        optional
            ISBNs to look up.

            .. note::

               Exactly one of `itunes_ids`, `amg_album_ids`,
               `amg_artist_ids`, `amg_video_ids`, `bundle_ids`, `isbns`,
               or `upcs` must be provided.

            **Examples**: :code:`9781449355739`, :code:`"9781449365035"`,
            :code:`[9781449355739, 9781449365035]`,
            :code:`["9781449355739", "9781449365035"]`.

        upcs : int, str, or Collection[int | str], keyword-only, \
        optional
            UPCs/EANs to look up.

            .. note::

               Exactly one of `itunes_ids`, `amg_album_ids`,
               `amg_artist_ids`, `amg_video_ids`, `bundle_ids`, `isbns`,
               or `upcs` must be provided.

            **Examples**: :code:`07464381122`, :code:`"888837724713"`,
            :code:`[07464381122, 888837724713]`,
            :code:`["07464381122", "888837724713"]`.

        entity : str, keyword-only, optional
            Type of resource to return.

            .. seealso::

               `Table 2-1 in the iTunes Search API Documentation
               (Archived) <https://developer.apple.com/library/archive
               /documentation/AudioVideo/Conceptual/iTuneSearchAPI
               /Searching.html#//apple_ref/doc/uid
               /TP40017632-CH5-SW2>`__ – Available entities.

            **Example**: :code:`"movieArtist"`.

        limit : int, keyword-only, optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`200`.

            **Default**: :code:`50`.

        sort : str, keyword-only, optional
            Sort applied to the lookup results.

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
                        "artistId": <int>,
                        "artistIds": <list[int]>,
                        "artistName": <str>,
                        "artistViewUrl": <str>,
                        "artworkUrl100": <str>,
                        "artworkUrl60": <str>,
                        "averageUserRating": <float>,
                        "currency": <str>,
                        "description": <str>,
                        "fileSizeBytes": <int>,
                        "formattedPrice": <str>,
                        "genreIds": <list[str]>,
                        "genres": <list[str]>,
                        "kind": <str>,
                        "price": <float>,
                        "releaseDate": <str>,
                        "trackCensoredName": <str>,
                        "trackId": <int>,
                        "trackName": <str>,
                        "trackViewUrl": <str>,
                        "userRatingCount": <int>
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
                        "kind": <str>,
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
                        "userRatingCount": 78314,
                        "userRatingCountForCurrentVersion": <int>,
                        "version": <str>,
                        "wrapperType": "software"
                      },
                      {
                        "artistId": <int>,
                        "artistName": <str>,
                        "artistViewUrl": <str>,
                        "artworkUrl100": <str>,
                        "artworkUrl30": <str>,
                        "artworkUrl60": <str>,
                        "artworkUrl600": <str>,
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
                        "feedUrl": <str>,
                        "genreIds": <list[str]>,
                        "genres": <list[str]>,
                        "isStreamable": <bool>,
                        "kind": <str>,
                        "longDescription": <str>,
                        "previewUrl": <str>,
                        "primaryGenreName": <str>,
                        "releaseDate": <str>,
                        "shortDescription": <str>,
                        "trackCensoredName": <str>,
                        "trackCount": <int>,
                        "trackExplicitness": <str>,
                        "trackHdPrice": <float>,
                        "trackHdRentalPrice": <float>,
                        "trackId": <int>,
                        "trackName": <str>,
                        "trackNumber": <int>,
                        "trackPrice": <float>,
                        "trackRentalPrice": <float>,
                        "trackTimeMillis": <int>,
                        "trackViewUrl": <str>,
                        "wrapperType": "track"
                      }
                    ]
                  }
        """
        params = {}
        seen = False
        local_variables = locals()
        for arg_name, param_name, numeric in [
            ("itunes_ids", "id", True),
            ("amg_album_ids", "amgAlbumId", True),
            ("amg_artist_ids", "amgArtistId", True),
            ("amg_video_ids", "amgVideoId", True),
            ("bundle_ids", "bundleId", False),
            ("isbns", "isbn", True),
            ("upcs", "upc", True),
        ]:
            if (arg := local_variables.get(arg_name)) is not None:
                if seen:
                    raise ValueError(
                        "Only one of `itunes_ids`, "
                        "`amg_album_ids`, `amg_artist_ids`, "
                        "`amg_video_ids`, `bundle_ids`, `isbns`, or "
                        "`upcs` can be provided."
                    )

                if not isinstance(arg, list | set | tuple):
                    arg = [arg]
                if numeric:
                    for val in arg:
                        if isinstance(val, str) and not val.isdigit():
                            raise ValueError(
                                f"Values in `{arg_name}` must be numeric."
                            )
                        elif not isinstance(val, int):
                            raise ValueError(
                                f"Values in `{arg_name}` must be numeric."
                            )
                else:
                    for val in arg:
                        if not isinstance(val, str) or not val.isalnum():
                            raise ValueError(
                                f"Values in `{arg_name}` must be alphanumeric."
                            )
                params[param_name] = ",".join(str(val) for val in arg)
                seen = True
        if entity is not None:
            self._validate_type("entity", entity, str)
            entities = self._MEDIA_RELATIONSHIPS["all"]["entities"]
            if entity not in entities:
                entities = "', '".join(entities)
                raise ValueError(
                    f"Invalid entity {entity!r}. Valid values: '{entities}'."
                )
        if limit is not None:
            self._validate_number("limit", limit, int, 1, 200)
            params["limit"] = limit
        if sort is not None:
            if sort != "recent":
                raise ValueError("Invalid sort value. Valid value: 'recent'.")
            params["sort"] = sort
        return self._request("GET", "lookup", params=params).json()

    @TTLCache.cached_method(ttl="search")
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
        language: str | None = None,
        version: int | None = None,
        explicit: bool | str | None = None,
    ) -> dict[str, Any]:
        """
        Search for content using a text string.

        Parameters
        ----------
        term : str, positional-only
            Search query.

            **Example**: :code:`"jack johnson"`.

        country : str
            ISO 3166-1 alpha-2 country code for the storefront to search
            in.

            **Default**: :code:`"US"`.

        media : str, keyword-only, optional
            Media type to search across.

            **Valid values**: :code:`"all"`, :code:`"audiobook"`,
            :code:`"ebook"`, :code:`"movie"`, :code:`"music"`,
            :code:`"musicVideo"`, :code:`"podcast"`,
            :code:`"shortFilm"`, :code:`"software"`, :code:`"tvShow"`.

            **Default**: :code:`"all"`.

        entity : str, keyword-only, optional
            Type of resource to return for the specified `media`.

            .. seealso::

               `Table 2-1 in the iTunes Search API Documentation
               (Archived) <https://developer.apple.com/library/archive
               /documentation/AudioVideo/Conceptual/iTuneSearchAPI
               /Searching.html#//apple_ref/doc/uid
               /TP40017632-CH5-SW2>`__ – Available entities for each
               media type.

            **Example**: :code:`"movieArtist"` when :code:`media="movie"`.

        attribute : str, keyword-only, optional
            Field to constrain the search by, depending on the specified
            `media`.

            .. seealso::

               `iTunes Search API Documentation (Apple Services
               Performance Partner Program)
               <https://performance-partners.apple.com/search-api>`__ –
               Available attributes for each media type.

            **Example**: :code:`"allArtistTerm"` when
            :code:`media="all"` and :code:`entity="allArtist"`.

        limit : int, keyword-only, optional
            Maximum number of items to return.

            **Valid range**: :code:`1` to :code:`200`.

            **Default**: :code:`50`.

        language : str, keyword-only, optional
            Locale identifier consisting of an ISO 639-1 language
            code and an ISO 3166-1 alpha-2 country code joined by an
            underscore. When this parameter is provided, search results
            are returned in the specified language.

            **Valid values**:

            .. container::

               * :code:`"en_us"` – English
               * :code:`"ja_jp"` – Japanese

            **Default**: :code:`"en_us"`.

        version : int, keyword-only, optional
            Search result key version.

            **Valid values**: :code:`1`, :code:`2`.

            **Default**: :code:`2`.

        explicit : bool | str, keyword-only, optional
            Whether to include explicit content in the search results.

            **Valid values**: :code:`"Yes"` (or :code:`True`),
            :code:`"No"` (or :code:`False`).

            **Default**: :code:`"Yes"`.

        Returns
        -------
        results : dict[str, Any]
            Search results.

            .. admonition:: Sample responses
               :class: dropdown

               .. tab:: :code:`version=1`

                  .. code::

                     {
                       "resultCount": <int>,
                       "results": [
                         {
                           "artistId": <int>,
                           "artistName": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl60": <str>,
                           "collectionId": <int>,
                           "copyright": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "itemExplicitness":<str>,
                           "itemId": <int>,
                           "itemLinkUrl": <str>,
                           "itemPrice": <str>,
                           "primaryGenreId": <int>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "wrapperType": "audiobook"
                         },
                         {
                           "amgArtistId": <int>,
                           "artistDisplayName": <str>,
                           "artistId": <int>,
                           "artistName": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl60": <str>,
                           "collectionId": <int>,
                           "copyright": <str>,
                           "country": <str>,
                           "currency": <str>,
                           "itemCensoredName": <str>,
                           "itemExplicitness": <str>,
                           "itemId": <int>,
                           "itemLinkUrl": <str>,
                           "itemName": <str>,
                           "itemPrice": <str>,
                           "primaryGenreId": <str>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "wrapperType": "playlist"
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
                         }
                       ]
                     }

               .. tab:: :code:`version=2`

                  .. code::

                     {
                       "resultCount": <int>,
                       "results": [
                         {
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
                           "artistId": <int>,
                           "artistIds": <list[int]>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl60": <str>,
                           "averageUserRating": <float>,
                           "currency": <str>,
                           "description": <str>,
                           "fileSizeBytes": <int>,
                           "formattedPrice": <str>,
                           "genreIds": <list[str]>,
                           "genres": <list[str]>,
                           "kind": <str>,
                           "price": <float>,
                           "releaseDate": <str>,
                           "trackCensoredName": <str>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackViewUrl": <str>,
                           "userRatingCount": <int>
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
                           "kind": <str>,
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
                         },
                         {
                           "artistId": <int>,
                           "artistName": <str>,
                           "artistViewUrl": <str>,
                           "artworkUrl100": <str>,
                           "artworkUrl30": <str>,
                           "artworkUrl60": <str>,
                           "artworkUrl600": <str>,
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
                           "feedUrl": <str>,
                           "genreIds": <list[str]>,
                           "genres": <list[str]>,
                           "isStreamable": <bool>,
                           "kind": <str>,
                           "longDescription": <str>,
                           "previewUrl": <str>,
                           "primaryGenreName": <str>,
                           "releaseDate": <str>,
                           "shortDescription": <str>,
                           "trackCensoredName": <str>,
                           "trackCount": <int>,
                           "trackExplicitness": <str>,
                           "trackHdPrice": <float>,
                           "trackHdRentalPrice": <float>,
                           "trackId": <int>,
                           "trackName": <str>,
                           "trackNumber": <int>,
                           "trackPrice": <float>,
                           "trackRentalPrice": <float>,
                           "trackTimeMillis": <int>,
                           "trackViewUrl": <str>,
                           "wrapperType": "track"
                         }
                       ]
                     }
        """
        self._validate_type("term", term, str)
        self._validate_type("country", country, str)
        if len(country) != 2 or not country.isalpha():
            raise ValueError(
                f"Invalid country code {country!r}. Must be a ISO "
                "3166-1 alpha-2 country code."
            )
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
        if language is not None:
            self._validate_locale(language)
            params["lang"] = language
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
        return self._request("GET", "search", params=params).json()

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

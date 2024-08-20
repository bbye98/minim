"""
iTunes
======
.. moduleauthor:: Benjamin Ye <GitHub: bbye98>

This module contains a complete implementation of all iTunes Search API
endpoints.
"""

import requests
from typing import Any, Union

__all__ = ["SearchAPI"]


class SearchAPI:
    """
    iTunes Search API client.

    The iTunes Search API allows searching for a variety of content,
    including apps, iBooks, movies, podcasts, music, music videos,
    audiobooks, and TV shows within the iTunes Store, App Store,
    iBooks Store and Mac App Store. It also supports ID-based lookup
    requests to create mappings between your content library and the
    digital catalog.

    .. seealso::

       For more information, see the `iTunes Search API
       documentation <https://developer.apple.com/library/archive/
       documentation/AudioVideo/Conceptual/iTuneSearchAPI/index.html>`_.

    Attributes
    ----------
    API_URL : `str`
        Base URL for the iTunes Search API.
    """

    API_URL = "https://itunes.apple.com"

    def __init__(self) -> None:
        """
        Create a iTunes Search API client.
        """

        self.session = requests.Session()

    def _get_json(self, url: str, **kwargs) -> dict:
        """
        Send a GET request and return the JSON-encoded content of the
        response.

        Parameters
        ----------
        url : `str`
            URL for the GET request.

        **kwargs
            Keyword arguments to pass to :meth:`requests.request`.

        Returns
        -------
        resp : `dict`
            JSON-encoded content of the response.
        """

        return self._request("get", url, **kwargs).json()

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Construct and send a request, but with status code checking.

        Parameters
        ----------
        method : `str`
            Method for the request.

        url : `str`
            URL for the request.

        **kwargs
            Keyword arguments passed to :meth:`requests.request`.

        Returns
        -------
        resp : `requests.Response`
            Response to the request.
        """

        r = self.session.request(method, url, **kwargs)
        if r.status_code not in range(200, 299):
            raise RuntimeError(f"{r.status_code} {r.json()['errorMessage']}")
        return r

    def search(
        self,
        term: str,
        *,
        country: str = None,
        media: str = None,
        entity: Union[str, list[str]] = None,
        attribute: str = None,
        limit: Union[int, str] = None,
        lang: str = None,
        version: Union[int, str] = None,
        explicit: Union[bool, str] = None,
    ) -> dict[str, Any]:
        """
        Search for content using the iTunes Search API.

        Parameters
        ----------
        term : str
            The text string to search for.

            .. note::

               URL encoding replaces spaces with the plus (:code:`+`)
               character, and all characters except letters, numbers,
               periods (:code:`.`), dashes (:code:`-`), underscores
               (:code:`_`), and asterisks (:code:`*`) are encoded.

            **Example**: :code:`"jack+johnson"`.

        country : str, keyword-only, optional
            The two-letter country code for the store you want to search.
            The search uses the default store front for the specified
            country.

            .. seealso::

               For a list of ISO country codes, see the
               `ISO OBP <https://www.iso.org/obp/ui>`_.

            **Default**: :code:`"US"`.

        media : str, keyword-only, optional
            The media type you want to search for.

            .. container::

               **Valid values**: :code:`"movie"`, :code:`"podcast"`,
               :code:`"music"`, :code:`"musicVideo"`, :code:`"audioBook"`,
               :code:`"shortFilm"`, :code:`"tvShow"`, :code:`"software"`,
               and :code:`"ebook"`.

            **Default**: :code:`"all"`.

        entity : `str` or `list`, keyword-only, optional
            The type(s) of results you want returned, relative to the
            specified media type in `media`.

            .. seealso::

               For a list of available
               entities, see the `iTunes Store API Table 2-1
               <https://developer.apple.com/library/archive
               /documentation/AudioVideo/Conceptual/iTuneSearchAPI
               /Searching.html#//apple_ref/doc/uid
               /TP40017632-CH5-SW2>`_.

            **Default**: The track entity associated with the specified
            media type.

            **Example**: :code:`"movieArtist"` for a movie media type
            search.

        attribute : `str`, keyword-only, optional
            The attribute you want to search for in the stores, relative
            to the specified media type (`media`).

            .. seealso::

               For a list of available
               attributes, see the `iTunes Store API Table 2-2
               <https://developer.apple.com/library/archive
               /documentation/AudioVideo/Conceptual/iTuneSearchAPI
               /Searching.html#//apple_ref/doc/uid
               /TP40017632-CH5-SW3>`_.

            **Default**: All attributes associated with the specified
            media type.

            **Example**: If you want to search for an artist by name,
            specify :code:`entity="allArtist"` and
            :code:`attribute="allArtistTerm"`. Then, if you search for
            :code:`term="maroon"`, iTunes returns "Maroon 5" in the
            search results, instead of all artists who have ever
            recorded a song with the word "maroon" in the title.

        limit : `int` or `str`, keyword-only, optional
            The number of search results you want the iTunes Store to
            return.

            **Valid values**: `limit` must be between 1 and 200.

            **Default**: :code:`50`.

        lang : `str`, keyword-only, optional
            The language, English or Japanese, you want to use when
            returning search results. Specify the language using the
            five-letter codename.

            .. container::

               **Valid values**:

               * :code:`"en_us"` for English.
               * :code:`"ja_jp"` for Japanese.

            **Default**: :code:`"en_us"`.

        version : `int` or `str`, keyword-only, optional
            The search result key version you want to receive back from
            your search.

            **Valid values**: :code:`1` and :code:`2`.

            **Default**: :code:`2`.

        explicit : `bool` or `str`, keyword-only, optional
            A flag indicating whether or not you want to include
            explicit content in your search results.

            **Default**: :code:`"Yes"`.

        Returns
        -------
        results : `dict`
            The search results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "resultCount": <int>,
                    "results": [
                      {
                        "wrapperType": <str>,
                        "kind": <str>,
                        "artistId": <int>,
                        "collectionId": <int>,
                        "trackId": <int>,
                        "artistName": <str>,
                        "collectionName": <str>,
                        "trackName": <str>,
                        "collectionCensoredName": <str>,
                        "trackCensoredName": <str>,
                        "collectionArtistId": <int>,
                        "collectionArtistName": <str>,
                        "artistViewUrl": <str>,
                        "collectionViewUrl": <str>,
                        "trackViewUrl": <str>,
                        "previewUrl": <str>,
                        "artworkUrl30": <str>,
                        "artworkUrl60": <str>,
                        "artworkUrl100": <str>,
                        "collectionPrice": <float>,
                        "trackPrice": <float>,
                        "releaseDate": <str>,
                        "collectionExplicitness": <str>,
                        "trackExplicitness": <str>,
                        "discCount": <int>,
                        "discNumber": <int>,
                        "trackCount": <int>,
                        "trackNumber": <int>,
                        "trackTimeMillis": <int>,
                        "country": <str>,
                        "currency": <str>,
                        "primaryGenreName": <str>,
                        "isStreamable": <bool>
                      }
                    ]
                  }

        Examples
        --------
        To search for all Jack Johnson audio and video content (movies,
        podcasts, music, music videos, audiobooks, short films, and TV
        shows),

        >>> itunes.search("jack johnson")

        To search for all Jack Johnson audio and video content and
        return only the first 25 items,

        >>> itunes.search("jack johnson", limit=25)

        To search for only Jack Johnson music videos,

        >>> itunes.search("jack johnson", entity="musicVideo")

        To search for all Jim Jones audio and video content and return
        only the results from the Canada iTunes Store,

        >>> itunes.search("jack johnson", country="ca")

        To search for applications titled “Yelp” and return only the
        results from the United States iTunes Store,

        >>> itunes.search("yelp", country="us", entity="software")
        """

        return self._get_json(
            f"{self.API_URL}/search",
            params={
                "term": term,
                "country": country,
                "media": media,
                "entity": (
                    entity
                    if entity is None or isinstance(entity, str)
                    else ",".join(entity)
                ),
                "attribute": attribute,
                "limit": limit,
                "lang": lang,
                "version": version,
                "explicit": (
                    ("No", "Yes")[explicit] if isinstance(explicit, bool) else explicit
                ),
            },
        )

    def lookup(
        self,
        id: Union[int, str, list[Union[int, str]]] = None,
        *,
        amg_artist_id: Union[int, str, list[Union[int, str]]] = None,
        amg_album_id: Union[int, str, list[Union[int, str]]] = None,
        amg_video_id: Union[int, str, list[Union[int, str]]] = None,
        bundle_id: Union[str, list[str]] = None,
        upc: Union[int, str, list[Union[int, str]]] = None,
        isbn: Union[int, str, list[Union[int, str]]] = None,
        entity: Union[str, list[str]] = None,
        limit: Union[int, str] = None,
        sort: str = None,
    ) -> dict[str, Any]:
        """
        Search for content based on iTunes IDs, AMG IDs, UPCs/EANs, or
        ISBNs. ID-based lookups are faster and contain fewer
        false-positive results.

        Parameters
        ----------
        id : `int`, `str`, or `list`, optional
            The iTunes ID(s) to lookup.

        amg_artist_id : `int`, `str`, or `list`, keyword-only, optional
            The AMG artist ID(s) to lookup.

        amg_album_id : `int`, `str`, or `list`, keyword-only, optional
            The AMG album ID(s) to lookup.

        amg_video_id : `int`, `str`, or `list`, keyword-only, optional
            The AMG video ID(s) to lookup.

        bundle_id : `str` or `list`, keyword-only, optional
            The Apple bundle ID(s) to lookup.

        upc : `int`, `str`, or `list`, keyword-only, optional
            The UPC(s) to lookup.

        isbn : `int`, `str`, or `list`, keyword-only, optional
            The 13-digit ISBN(s) to lookup.

        entity : `str` or `list`, keyword-only, optional
            The type(s) of results you want returned.

            .. seealso::

               For a list of available entities, see the `iTunes Store
               API Table 2-1 <https://developer.apple.com/library
               /archive/documentation/AudioVideo/Conceptual
               /iTuneSearchAPI/Searching.html#//apple_ref/doc/uid
               /TP40017632-CH5-SW2>`_.

            **Default**: The track entity associated with the specified
            media type.

        limit : `int` or `str`, keyword-only, optional
            The number of search results you want the iTunes Store to
            return.

            **Valid values**: `limit` must be between 1 and 200.

            **Default**: :code:`50`.

        sort : `str`, keyword-only, optional
            The sort applied to the search results.

            **Allowed value**: :code:`"recent"`.

        Returns
        -------
        results : `dict`
            The lookup results.

            .. admonition:: Sample response
               :class: dropdown

               .. code::

                  {
                    "resultCount": <int>,
                    "results": [
                      {
                        "wrapperType": <str>,
                        "kind": <str>,
                        "artistId": <int>,
                        "collectionId": <int>,
                        "trackId": <int>,
                        "artistName": <str>,
                        "collectionName": <str>,
                        "trackName": <str>,
                        "collectionCensoredName": <str>,
                        "trackCensoredName": <str>,
                        "collectionArtistId": <int>,
                        "collectionArtistName": <str>,
                        "artistViewUrl": <str>,
                        "collectionViewUrl": <str>,
                        "trackViewUrl": <str>,
                        "previewUrl": <str>,
                        "artworkUrl30": <str>,
                        "artworkUrl60": <str>,
                        "artworkUrl100": <str>,
                        "collectionPrice": <float>,
                        "trackPrice": <float>,
                        "releaseDate": <str>,
                        "collectionExplicitness": <str>,
                        "trackExplicitness": <str>,
                        "discCount": <int>,
                        "discNumber": <int>,
                        "trackCount": <int>,
                        "trackNumber": <int>,
                        "trackTimeMillis": <int>,
                        "country": <str>,
                        "currency": <str>,
                        "primaryGenreName": <str>,
                        "isStreamable": <bool>
                      }
                    ]
                  }

        Examples
        --------
        Look up Jack Johnson by iTunes artist ID:

        >>> itunes.lookup(909253)

        Look up the Yelp application by iTunes ID:

        >>> itunes.lookup(284910350)

        Look up Jack Johnson by AMG artist ID:

        >>> itunes.lookup(amg_artist_id=468749)

        Look up multiple artists by their AMG artist IDs:

        >>> itunes.lookup(amg_artist_id=[468749, 5723])

        Look up all albums for Jack Johnson:

        >>> itunes.lookup(909253, entity="album")

        Look up multiple artists by their AMG artist IDs and get each
        artist's top 5 albums:

        >>> itunes.lookup(amg_artist_id=[468749, 5723], entity="album",
        ...               limit=5)

        Look up multiple artists by their AMG artist IDs and get each
        artist's 5 most recent songs:

        >>> itunes.lookup(amg_artist_id=[468749, 5723], entity="song",
        ...               limit=5, sort="recent")

        Look up an album or video by its UPC:

        >>> itunes.lookup(upc=720642462928)

        Look up an album by its UPC, including the tracks on that album:

        >>> itunes.lookup(upc=720642462928, entity="song")

        Look up an album by its AMG Album ID:

        >>> itunes.lookup(amg_album_id=[15175, 15176, 15177, 15178,
        ...                             15183, 15184, 15187, 15190,
        ...                             15191, 15195, 15197, 15198])

        Look up a Movie by AMG Video ID:

        >>> itunes.lookup(amg_video_id=17120)

        Look up a book by its 13-digit ISBN:

        >>> itunes.lookup(isbn=9780316069359)

        Look up the Yelp application by iTunes bundle ID:

        >>> itunes.lookup(bundle_id="com.yelp.yelpiphone")
        """

        return self._get_json(
            f"{self.API_URL}/lookup",
            params={
                "id": (
                    id
                    if id is None or isinstance(id, (int, str))
                    else ",".join(
                        id if isinstance(id[0], str) else (str(i) for i in id)
                    )
                ),
                "amgArtistId": (
                    amg_artist_id
                    if amg_artist_id is None or isinstance(amg_artist_id, (int, str))
                    else ",".join(
                        amg_artist_id
                        if isinstance(amg_artist_id[0], str)
                        else (str(i) for i in amg_artist_id)
                    )
                ),
                "amgAlbumId": (
                    amg_album_id
                    if amg_album_id is None or isinstance(amg_album_id, (int, str))
                    else ",".join(
                        amg_album_id
                        if isinstance(amg_album_id[0], str)
                        else (str(i) for i in amg_album_id)
                    )
                ),
                "amgVideoId": (
                    amg_video_id
                    if amg_video_id is None or isinstance(amg_video_id, (int, str))
                    else ",".join(
                        amg_video_id
                        if isinstance(amg_video_id[0], str)
                        else (str(i) for i in amg_video_id)
                    )
                ),
                "bundleId": (
                    bundle_id
                    if bundle_id is None or isinstance(bundle_id, str)
                    else ",".join(bundle_id)
                ),
                "upc": (
                    upc
                    if upc is None or isinstance(upc, (int, str))
                    else ",".join(
                        upc if isinstance(upc[0], str) else (str(u) for u in upc)
                    )
                ),
                "isbn": (
                    isbn
                    if isbn is None or isinstance(isbn, (int, str))
                    else ",".join(
                        isbn if isinstance(isbn[0], str) else (str(i) for i in isbn)
                    )
                ),
                "entity": (
                    entity
                    if entity is None or isinstance(entity, str)
                    else ",".join(entity)
                ),
                "limit": limit,
                "sort": sort,
            },
        )

from collections.abc import Collection
from datetime import datetime
from functools import cached_property
from json.decoder import JSONDecodeError
import time
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse
import warnings

from .._shared import OAuth2APIClient
from ._web_api.albums import AlbumsAPI
from ._web_api.artists import ArtistsAPI
from ._web_api.audiobooks import AudiobooksAPI
from ._web_api.categories import CategoriesAPI
from ._web_api.chapters import ChaptersAPI
from ._web_api.episodes import EpisodesAPI
from ._web_api.genres import GenresAPI
from ._web_api.markets import MarketsAPI
from ._web_api.player import PlayerAPI
from ._web_api.playlists import PlaylistsAPI
from ._web_api.search import SearchAPI
from ._web_api.shows import ShowsAPI
from ._web_api.tracks import TracksAPI
from ._web_api.users import UsersAPI

if TYPE_CHECKING:
    import httpx


class SpotifyWebAPI(OAuth2APIClient):
    """
    Spotify Web API client.
    """

    _AUDIO_TYPES = {"episode", "track"}
    _ENV_VAR_PREFIX = "SPOTIFY_WEB_API"
    _FLOWS = {"auth_code", "pkce", "client_credentials"}
    _PROVIDER = "Spotify"
    _QUAL_NAME = "minim.api.spotify.SpotifyWebAPI"
    _SCOPES = {
        "images": {"ugc-image-upload"},
        "spotify_connect": {
            "user-read-playback-state",
            "user-modify-playback-state",
            "user-read-currently-playing",
        },
        "playback": {"app-remote-control", "streaming"},
        "playlists": {
            "playlist-read-private",
            "playlist-read-collaborative",
            "playlist-modify-private",
            "playlist-modify-public",
        },
        "follow": {"user-follow-modify", "user-follow-read"},
        "listening_history": {
            "user-read-playback-position",
            "user-top-read",
            "user-read-recently-played",
        },
        "library": {"user-library-modify", "user-library-read"},
        "users": {"user-read-email", "user-read-private"},
    }
    AUTH_URL = "https://accounts.spotify.com/authorize"
    BASE_URL = "https://api.spotify.com/v1"
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(
        self,
        *,
        flow: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        scopes: str | Collection[str] = "",
        access_token: str | None = None,
        token_type: str = "Bearer",
        refresh_token: str | None = None,
        expiry: str | datetime | None = None,
        backend: str | None = None,
        browser: bool = False,
        cache: bool = True,
        store: bool = True,
        user_identifier: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        flow : str, keyword-only
            Authorization flow.

            .. container::

               **Valid values**:

               * :code:`"auth_code"` – Authorization Code Flow.
               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` – Client Credentials Flow.

        client_id : str, keyword-only, optional
            Client ID. Must be provided unless it is set as system
            environment variable :code:`SPOTIFY_WEB_API_CLIENT_ID` or
            stored in Minim's local token storage.

        client_secret : str, keyword-only, optional
            Client secret. Required for the Authorization Code and
            Client Credentials flows and must be provided unless it is
            set as system environment variable
            :code:`SPOTIFY_WEB_API_CLIENT_SECRET` or stored in Minim's
            local token storage.

        redirect_uri : str, keyword-only, optional
            Redirect URI. Required for the Authorization Code and
            Authorization Code with PKCE flows. If the host is not
            :code:`127.0.0.1`, redirect handling is not available.

        scopes : str or Collection[str], keyword-only, optional
            Authorization scopes the client requests to access user
            resources.

            .. seealso::

               :meth:`get_scopes` – Get a set of scopes to request,
               filtered by categories and/or substrings.

        access_token : str, keyword-only, optional
            Access token. If provided or found in Minim's local token
            storage, the authorization process is bypassed. If provided,
            all other relevant keyword arguments should also be
            specified to enable automatic token refresh upon expiration.

        token_type : str, keyword-only, default: :code:`"Bearer"`
            Type of the access token.

        refresh_token : str, keyword-only, optional
            Refresh token accompanying the access token in
            `access_token`. If not provided, the user will be
            reauthorized via the authorization flow in `flow` when the
            access token expires.

        expiry : str or datetime.datetime, keyword-only, optional
            Expiry of the access token in `access_token`. If provided as
            a string, it must be in ISO 8601 format
            (:code:`%Y-%m-%dT%H:%M:%SZ`).

        backend : str, keyword-only, optional
            Backend to handle redirects during the authorization flow.

            .. container::

               **Valid values**:

               * :code:`None` – Manually paste the redirect URL into
                 the terminal.
               * :code:`"http.server"` – Simple HTTP server.
               * :code:`"playwright"` – Playwright Firefox browser.

        browser : bool, keyword-only, default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the Authorization Code and
            Authorization Code with PKCE flows. If :code:`False`, the
            authorization URL is printed to the terminal.

        cache : bool, keyword-only, default: :code:`True`
            Whether to enable an in-memory time-to-live (TTL) cache with
            a least recently used (LRU) eviction policy for this client.

        store : bool, keyword-only, default: :code:`True`
            Whether to enable Minim's local token storage for this
            client. If :code:`True`, newly acquired access tokens and
            related information are stored. If :code:`False`, the client
            will not retrieve or store access tokens.

        user_identifier : str, keyword-only, optional
            Unique identifier for the user account to log into for all
            authorization flows but the Client Credentials flow. Used
            when :code:`store=True` to distinguish between multiple
            user accounts for the same client ID and authorization flow.

            If provided, it is used to locate existing access tokens or
            store new tokens in Minim's local token storage, where the
            key is a SHA-256 hash of the client ID, authorization flow,
            and the identifier.

            If not provided, the last accessed account for the specified
            authorization flow in `flow` is selected if it exists in
            local storage. Otherwise, a new entry is created using a
            hash of the client ID, authorization flow, and the Spotify
            user ID.

            Prepending the identifier with a tilde (:code:`~`) skips
            token retrieval from local storage and forces a
            reauthorization.
        """
        # Initialize subclasses for categorized endpoints
        #: Albums API endpoints for the Spotify Web API.
        self.albums: AlbumsAPI = AlbumsAPI(self)
        #: Artists API endpoints for the Spotify Web API.
        self.artists: ArtistsAPI = ArtistsAPI(self)
        #: Audiobooks API endpoints for the Spotify Web API.
        self.audiobooks: AudiobooksAPI = AudiobooksAPI(self)
        #: Categories API endpoints for the Spotify Web API.
        self.categories: CategoriesAPI = CategoriesAPI(self)
        #: Chapters API endpoints for the Spotify Web API.
        self.chapters: ChaptersAPI = ChaptersAPI(self)
        #: Episodes API endpoints for the Spotify Web API.
        self.episodes: EpisodesAPI = EpisodesAPI(self)
        #: Genres API endpoints for the Spotify Web API.
        self.genres: GenresAPI = GenresAPI(self)
        #: Markets API endpoints for the Spotify Web API.
        self.markets: MarketsAPI = MarketsAPI(self)
        #: Player API endpoints for the Spotify Web API.
        self.player: PlayerAPI = PlayerAPI(self)
        #: Playlists API endpoints for the Spotify Web API.
        self.playlists: PlaylistsAPI = PlaylistsAPI(self)
        #: Search API endpoints for the Spotify Web API.
        self.search: SearchAPI = SearchAPI(self)
        #: Shows API endpoints for the Spotify Web API.
        self.shows: ShowsAPI = ShowsAPI(self)
        #: Tracks API endpoints for the Spotify Web API.
        self.tracks: TracksAPI = TracksAPI(self)
        #: Users API endpoints for the Spotify Web API.
        self.users: UsersAPI = UsersAPI(self)

        if flow == "client_credentials" and scopes:
            warnings.warn(
                f"The {self._OAUTH_FLOWS_NAMES['client_credentials']} "
                "in the Spotify Web API does not support scopes."
            )
            scopes = ""

        if urlparse(redirect_uri).scheme == "http":
            raise ValueError(
                "Redirect URIs using the HTTP scheme are not supported "
                "by the Spotify Web API."
            )

        super().__init__(
            flow=flow,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scopes=scopes,
            access_token=access_token,
            token_type=token_type,
            refresh_token=refresh_token,
            expiry=expiry,
            backend=backend,
            browser=browser,
            cache=cache,
            store=store,
            user_identifier=user_identifier,
        )

    @classmethod
    def get_scopes(
        cls, matches: str | Collection[str] | None = None
    ) -> set[str]:
        """
        Resolve one or more scope categories or substrings into a set of
        scopes.

        Parameters
        ----------
        matches : str or Collection[str], optional
            Categories and/or substrings to filter scopes by.

            .. container::

               **Valid values**:

               * :code:`"images"` – Scopes related to custom images,
                 such as :code:`ugc-image-upload`.
               * :code:`"spotify_connect"` – Scopes related to Spotify
                 Connect, such as

                 * :code:`user-read-playback-state`,
                 * :code:`user-modify-playback-state`, and
                 * :code:`user-read-currently-playing`.
               * :code:`"playback"` – Scopes related to playback
                 control, such as :code:`app-remote-control` and
                 :code:`streaming`.
               * :code:`"playlists"` – Scopes related to playlists, such
                 as

                 * :code:`playlist-read-private`,
                 * :code:`playlist-read-collaborative`,
                 * :code:`playlist-modify-private`, and
                 * :code:`playlist-modify-public`.
               * :code:`"follow"` – Scopes related to followed artists
                 and users, such as :code:`user-follow-modify` and
                 :code:`user-follow-read`.
               * :code:`"listening_history"` – Scopes related to
                 playback history, such as

                 * :code:`user-read-playback-position`,
                 * :code:`user-top-read`, and
                 * :code:`user-read-recently-played`.
               * :code:`"library"` – Scopes related to saved content,
                 such as :code:`user-library-modify` and
                 :code:`user-library-read`.
               * :code:`"users"` – Scopes related to user information,
                 such as :code:`user-read-email` and
                 :code:`user-read-private`.
               * :code:`None` for all scopes above.
               * A substring to match in the available scopes.

                 * :code:`"read"` – All scopes above that grant read
                   access, i.e., scopes with :code:`read` in the name.
                 * :code:`"modify"` – All scopes above that grant
                   modify access, i.e., scopes with :code:`modify` in
                   the name.
                 * :code:`"user"` – All scopes above that grant access
                   to all user-related information, i.e., scopes with
                   :code:`user` in the name.

        Returns
        -------
        scopes : set[str]
            Authorization scopes.
        """
        # Return all scopes if no matches are provided
        if matches is None:
            return set().union(*cls._SCOPES.values())

        if isinstance(matches, str):
            # Return scopes for a specific category
            if matches in cls._SCOPES:
                return cls._SCOPES[matches]

            # Return scopes containing a substring
            return {
                scope
                for scopes in cls._SCOPES.values()
                for scope in scopes
                if matches in scope
            }

        # Recursively gather scopes for multiple
        # categories/substrings
        return {scope for match in matches for scope in cls.get_scopes(match)}

    @staticmethod
    def _prepare_spotify_ids(
        spotify_ids: str | Collection[str],
        /,
        *,
        limit: int,
        strict_length: bool = True,
    ) -> tuple[str, int]:
        """
        Stringify a list of Spotify IDs into a comma-delimited string.

        Parameters
        ----------
        spotify_ids : str or Collection[str], positional-only
            (Comma-delimited) list of Spotify IDs.

        limit : int, keyword-only
            Maximum number of Spotify IDs that can be sent in the
            request.

        strict_length : bool, keyword-only, default: :code:`True`
            Whether to only allow 22-character-long Spotify IDs.

        Returns
        -------
        spotify_ids : str
            Comma-delimited string containing Spotify IDs.

        n_ids : int
            Number of Spotify IDs.
        """
        if not spotify_ids:
            raise ValueError("At least one Spotify ID must be specified.")

        if isinstance(spotify_ids, str):
            return SpotifyWebAPI._prepare_spotify_ids(
                spotify_ids.split(","), limit=limit, strict_length=strict_length
            )

        n_ids = len(spotify_ids)
        if n_ids > limit:
            raise ValueError(
                f"A maximum of {limit} Spotify IDs can be sent in one request."
            )
        for idx, id_ in enumerate(spotify_ids):
            spotify_ids[idx] = id_ = id_.strip()
            SpotifyWebAPI._validate_spotify_id(id_, strict_length=strict_length)
        return ",".join(spotify_ids), n_ids

    @staticmethod
    def _prepare_spotify_uris(
        spotify_uris: str | Collection[str],
        /,
        *,
        limit: int,
        item_types: Collection[str],
    ) -> list[str]:
        """
        Prepare a list of Spotify Uniform Resource Identifiers (URIs) to
        include in the body of a HTTP request.

        Parameters
        ----------
        spotify_uris : str or Collection[str], positional-only
            (Comma-delimited) list of Spotify URIs.

        limit : int, keyword-only
            Maximum number of Spotify URIs that can be sent in the
            request.

        item_types : Collection[str]
            Allowed Spotify item types.

        Returns
        -------
        spotify_uris : list[str]
            List of Spotify URIs.
        """
        if not spotify_uris:
            raise ValueError("At least one Spotify URI must be specified.")

        if isinstance(spotify_uris, str):
            return SpotifyWebAPI._prepare_spotify_uris(
                spotify_uris.split(","), limit=limit, item_types=item_types
            )

        if len(spotify_uris) > limit:
            raise ValueError(
                f"A maximum of {limit} Spotify URIs can be sent in one request."
            )
        for idx, uri in enumerate(spotify_uris):
            spotify_uris[idx] = uri = uri.strip()
            SpotifyWebAPI._validate_spotify_uri(uri, item_types=item_types)
        return spotify_uris

    @staticmethod
    def _validate_spotify_id(
        spotify_id: str, /, *, strict_length: bool = True
    ) -> None:
        """
        Validate a Spotify ID.

        Parameters
        ----------
        spotify_id : str
            Spotify ID.

        strict_length : bool, keyword-only, default: :code:`True`
            Whether to only allow 22-character-long Spotify IDs.
        """
        if (
            not isinstance(spotify_id, str)
            or strict_length
            and len(spotify_id) != 22
            or not spotify_id.isalnum()
        ):
            raise ValueError(f"Invalid Spotify ID {spotify_id!r}.")

    @staticmethod
    def _validate_spotify_uri(
        spotify_uri: str, /, *, item_types: Collection[str]
    ) -> None:
        """
        Validate a Spotify Uniform Resource Identifier (URI).

        Parameters
        ----------
        spotify_uri : str
            Spotify URI.

        item_types : Collection[str]
            Allowed Spotify item types.
        """
        if (
            not isinstance(spotify_uri, str)
            or len(uri_parts := spotify_uri.split(":")) != 3
            or uri_parts[0] != "spotify"
            or uri_parts[1] not in item_types
            or len(spotify_id := uri_parts[2]) != 22
            or not spotify_id.isalnum()
        ):
            raise ValueError(f"Invalid Spotify URI {spotify_uri!r}.")

    @cached_property
    def available_seed_genres(self) -> list[str]:
        """
        Available seed genres for track recommendations.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 27, 2024
                  Access the
                  :code:`/recommendations/available-genre-seeds`
                  endpoint. `Learn more. <https://developer.spotify.com
                  /blog/2024-11-27-changes-to-the-web-api>`__

        .. note::

           Accessing this property for the first time may call
           :meth:`~minim.api.spotify.GenresAPI.get_available_seed_genres`
           and make a request to the Spotify Web API.
        """
        return self.genres.get_available_seed_genres()["genres"]

    @cached_property
    def available_markets(self) -> list[str]:
        """
        Markets where Spotify is available.

        .. note::

           Accessing this property for the first time may call
           :meth:`~minim.api.spotify.MarketsAPI.get_available_markets`
           and make a request to the Spotify Web API.
        """
        return self.markets.get_available_markets()["markets"]

    @cached_property
    def my_profile(self) -> dict[str, Any] | None:
        """
        Current user's profile.

        .. note::

           Accessing this property for the first time may call
           :meth:`~minim.api.users.UsersAPI.get_user_profile`.
        """
        if self._flow != "client_credentials":
            return self.users.get_user_profile()

    def _get_user_identifier(self) -> str:
        """
        Assign the Spotify user ID as the user identifier for the
        current account.
        """
        return self.my_profile["id"]

    def _prepare_audio_types(self, types: str | Collection[str], /) -> str:
        """
        Stringify a list of Spotify item types into a comma-delimited
        string.

        Parameters
        ----------
        types : str, positional-only
            Spotify item types.

        Returns
        -------
        types : str
            Comma-delimited string containing Spotify item types.
        """
        if isinstance(types, str):
            return self._prepare_audio_types(types.split(","))

        types = set(types)
        for type_ in types:
            if type_ not in self._AUDIO_TYPES:
                _types = "', '".join(self._AUDIO_TYPES)
                raise ValueError(
                    f"Invalid Spotify item type {type_!r}. "
                    f"Valid values: '{_types}'."
                )
        return ",".join(sorted(types))

    def _request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        retry: bool = True,
        **kwargs: dict[str, Any],
    ) -> "httpx.Response":
        """
        Make an HTTP request to a Spotify Web API endpoint.

        Parameters
        ----------
        method : str, positional-only
            HTTP method.

        endpoint : str, positional-only
            Spotify Web API endpoint.

        retry : bool, keyword-only, default: :code:`True`
            Whether to retry the request if the first attempt returns a
            :code:`401 Unauthorized` or :code:`429 Too Many Requests`.

        **kwargs : dict[str, Any]
            Keyword arguments to pass to :meth:`httpx.Client.request`.

        Returns
        -------
        response : httpx.Response
            HTTP response.
        """
        if self._expiry and datetime.now() > self._expiry:
            self._refresh_access_token()

        resp = self._client.request(method, endpoint, **kwargs)
        if not 200 <= (status := resp.status_code) < 300:
            if status == 401 and not self._expiry and retry:
                self._refresh_access_token()
                return self._request(method, endpoint, retry=False, **kwargs)
            if status == 429 and retry:
                retry_after = int(resp.headers.get("Retry-After", 0)) + 1
                warnings.warn(
                    "Rate limit exceeded. Retrying after "
                    f"{retry_after} second(s)."
                )
                time.sleep(retry_after)
                return self._request(method, endpoint, retry=False, **kwargs)
            emsg = f"{status} {resp.reason_phrase}"
            try:
                details = resp.json()["error"]["message"]
            except JSONDecodeError:
                # Fallback for users without access to apps in
                # development mode
                details = resp.text
            if details:
                emsg += f" – {details}"
            raise RuntimeError(emsg)
        return resp

    def _require_spotify_premium(self, endpoint_method: str) -> None:
        """
        Ensure that a Spotify Premium subscription is active for an
        endpoint method that requires it.

        Parameters
        ----------
        endpoint_method : str
            Name of the endpoint method.
        """
        if (
            self._flow == "client_credentials"
            or "my_profile" in self.__dict__
            and self.my_profile["product"] != "premium"
        ):
            raise RuntimeError(
                f"{self._QUAL_NAME}.{endpoint_method}() requires "
                "an active Spotify Premium subscription."
            )

    def _validate_market(self, market: str, /) -> None:
        """
        Validate market.

        Parameters
        ----------
        market : str, positional-only
            ISO 3166-1 alpha-2 country code.
        """
        if (
            not isinstance(market, str)
            or "markets" in self.__dict__
            and market not in self.available_markets
        ):
            _markets = "', '".join(self.available_markets)
            raise ValueError(
                f"{market!r} is not a market in which Spotify is "
                f"available. Valid values: '{_markets}'."
            )

    def _validate_seed_genre(self, seed_genre: str, /) -> None:
        """
        Validate seed genre.

        Parameters
        ----------
        seed_genre : str, positional-only
            Seed genre.
        """
        if (
            not isinstance(seed_genre, str)
            or "available_seed_genres" in self.__dict__
            and seed_genre not in self.available_seed_genres
        ):
            _genres = "', '".join(self.available_seed_genres)
            raise ValueError(
                f"Invalid seed genre {seed_genre!r}. Valid values: '{_genres}'."
            )

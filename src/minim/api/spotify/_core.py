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

    _ALLOWED_AUTH_FLOWS = {"auth_code", "pkce", "client_credentials"}
    _ALLOWED_SCOPES = {
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
    _ENV_VAR_PREFIX = "SPOTIFY_WEB_API"
    _PROVIDER = "Spotify"
    _QUAL_NAME = f"minim.api.{_PROVIDER.lower()}.{__qualname__}"
    AUTH_URL = "https://accounts.spotify.com/authorize"
    BASE_URL = "https://api.spotify.com/v1"
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(
        self,
        *,
        authorization_flow: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        scopes: str | set[str] = "",
        access_token: str | None = None,
        refresh_token: str | None = None,
        expires_at: str | datetime | None = None,
        redirect_handler: str | None = None,
        open_browser: bool = False,
        enable_cache: bool = True,
        store_tokens: bool = True,
        user_agent: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        authorization_flow : str; keyword-only
            Authorization flow.

            **Valid values**:

            .. container::

               * :code:`"auth_code"` – Authorization Code Flow.
               * :code:`"pkce"` – Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` – Client Credentials Flow.

        client_id : str; keyword-only; optional
            Client ID. Required unless set as system environment
            variable :code:`SPOTIFY_WEB_API_CLIENT_ID` or stored in the
            local token storage.

        client_secret : str; keyword-only; optional
            Client secret. Required for the Authorization Code and
            Client Credentials flows unless set as system environment
            variable :code:`SPOTIFY_WEB_API_CLIENT_SECRET` or stored in
            the local token storage.

        user_identifier : str; keyword-only; optional
            Identifier for the user account. Used when
            :code:`store_tokens=True` to distinguish between multiple
            accounts for the same client ID and authorization flow.

            If provided, it is used with the client ID and authorization
            flow to locate a matching stored token. If none is found, a
            new token is obtained and stored under this identifier.

            If not provided, the most recently accessed token for the
            client ID and authorization flow is used. If none exists, a
            new token is obtained and stored using the Spotify user ID
            acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        redirect_uri : str; keyword-only; optional
            Redirect URI. Required for the Authorization Code and
            Authorization Code with PKCE flows.

        scopes : str or set[str]; keyword-only; optional
            Authorization scopes requested by the client to access user
            resources.

            .. seealso::

               :meth:`resolve_scopes` – Resolve scope categories and/or
               substrings into a set of scopes.

        access_token : str; keyword-only; optional
            Access token. If provided, the authorization process is
            bypassed, and automatic token refresh is enabled when
            relevant metadata (refresh token, expiry, etc.) is also
            supplied.

        refresh_token : str; keyword-only; optional
            Refresh token for renewing the access token. If not
            provided, the user will be reauthorized via the specified
            authorization flow when the access token expires.

        expires_at : str or datetime.datetime; keyword-only; optional
            Expiration time of the access token. If a string, it must be
            in ISO 8601 format (:code:`%Y-%m-%dT%H:%M:%SZ`).

        redirect_handler : str or None; keyword-only; optional
            Backend for handling redirects during the authorization
            flow. Redirect handling is only available for hosts
            :code:`localhost`, :code:`127.0.0.1`, or :code:`::1`.

            **Valid values**:

            .. container::

               * :code:`None` – Show authorization URL in and have the
                 user manually paste the redirect URL into the terminal.
               * :code:`"http.server"` – Run a HTTP server to intercept
                 the redirect after user authorization in any local
                 browser.
               * :code:`"playwright"` – Use a Playwright Firefox
                 browser to complete the user authorization.

        open_browser : bool; keyword-only; default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the Authorization Code and
            Authorization Code with PKCE flows. If :code:`False`, the
            URL is printed to the terminal.

        enable_cache : bool; keyword-only; default: :code:`True`
            Whether to enable an in-memory time-to-live (TTL) cache with
            a least recently used (LRU) eviction policy for this client.
            If :code:`True`, responses from semi-static endpoints are
            cached for 2 minutes to 1 day, depending on their expected
            update frequency.

            .. seealso::

               :meth:`clear_cache` – Clear specific or all cache
               entries for this client.

        store_tokens : bool; keyword-only; default: :code:`True`
            Whether to enable the local token storage for this client.
            If :code:`True`, existing access tokens are retrieved when
            found in local storage, and newly acquired tokens and their
            metadata are stored for future retrieval. If :code:`False`,
            the client neither retrieves nor stores access tokens.

            .. seealso::

               :meth:`get_tokens` – Retrieve specific or all stored
               access tokens for this client.

               :meth:`remove_tokens` – Remove specific or all stored
               access tokens for this client.

        user_agent : str; keyword-only; optional
            :code:`User-Agent` value to include in the headers of HTTP
            requests.
        """
        if urlparse(redirect_uri).scheme == "http":
            raise ValueError(
                "Redirect URIs using the HTTP scheme are not supported "
                "by the Spotify Web API."
            )

        # Initialize subclasses for endpoint groups
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

        super().__init__(
            authorization_flow=authorization_flow,
            client_id=client_id,
            client_secret=client_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            scopes=scopes,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            redirect_handler=redirect_handler,
            open_browser=open_browser,
            enable_cache=enable_cache,
            store_tokens=store_tokens,
            user_agent=user_agent,
        )

    @classmethod
    def resolve_scopes(
        cls, matches: str | list[str] | None = None
    ) -> set[str]:
        """
        Resolve one or more scope categories or substrings into a set of
        scopes.

        Parameters
        ----------
        matches : str or list[str]; optional
            Categories and/or substrings to filter scopes by. If not
            specified, all available scopes are returned.

            **Valid values**:

            .. container::

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
            return set().union(*cls._ALLOWED_SCOPES.values())

        if isinstance(matches, str):
            # Return scopes for a specific category
            if matches in cls._ALLOWED_SCOPES:
                return cls._ALLOWED_SCOPES[matches]

            # Return scopes containing a substring
            return {
                scope
                for scopes in cls._ALLOWED_SCOPES.values()
                for scope in scopes
                if matches in scope
            }

        # Recursively gather scopes for multiple
        # categories/substrings
        return {
            scope for match in matches for scope in cls.resolve_scopes(match)
        }

    @staticmethod
    def _prepare_spotify_ids(
        spotify_ids: str | list[str],
        /,
        *,
        limit: int,
        enforce_length: bool = True,
    ) -> tuple[str, int]:
        """
        Normalize, validate, and serialize Spotify IDs.

        Parameters
        ----------
        spotify_ids : str or list[str]; positional-only
            Comma-separated string or list of Spotify IDs.

        limit : int; keyword-only
            Maximum number of Spotify IDs that can be sent in the
            request.

        enforce_length : bool; keyword-only; default: :code:`True`
            Whether to enforce the canonical 22-character Spotify ID
            length.

        Returns
        -------
        spotify_ids : str
            Comma-separated string of Spotify IDs.

        num_ids : int
            Number of Spotify IDs.
        """
        if not spotify_ids:
            raise ValueError("At least one Spotify ID must be specified.")

        if isinstance(spotify_ids, str):
            return SpotifyWebAPI._prepare_spotify_ids(
                spotify_ids.strip().split(","),
                limit=limit,
                enforce_length=enforce_length,
            )

        num_ids = len(spotify_ids)
        if num_ids > limit:
            raise ValueError(
                f"A maximum of {limit} Spotify IDs can be sent in a request."
            )
        spotify_ids_ = []
        for id_ in spotify_ids:
            id_ = id_.strip()
            SpotifyWebAPI._validate_spotify_id(
                id_, enforce_length=enforce_length
            )
            spotify_ids_.append(id_)
        return ",".join(spotify_ids_), num_ids

    @staticmethod
    def _prepare_spotify_uris(
        spotify_uris: str | list[str],
        /,
        *,
        limit: int,
        resource_types: set[str],
    ) -> list[str]:
        """
        Normalize, validate, and prepare Spotify Uniform Resource
        Identifiers (URIs).

        Parameters
        ----------
        spotify_uris : str or list[str]; positional-only
            Comma-separated string or list of Spotify URIs.

        limit : int; keyword-only
            Maximum number of Spotify URIs that can be sent in the
            request.

        resource_types : set[str]
            Allowed Spotify resource types.

        Returns
        -------
        spotify_uris : list[str]
            List of Spotify URIs.
        """
        if not spotify_uris:
            raise ValueError("At least one Spotify URI must be specified.")

        if isinstance(spotify_uris, str):
            return SpotifyWebAPI._prepare_spotify_uris(
                spotify_uris.strip().split(","),
                limit=limit,
                resource_types=resource_types,
            )

        if len(spotify_uris) > limit:
            raise ValueError(
                f"A maximum of {limit} Spotify URIs can be sent in a request."
            )
        spotify_uris_ = []
        for uri in spotify_uris:
            uri = uri.strip()
            SpotifyWebAPI._validate_spotify_uri(
                uri, resource_types=resource_types
            )
            spotify_uris_.append(uri)
        return spotify_uris

    @staticmethod
    def _validate_spotify_id(
        spotify_id: str, /, *, enforce_length: bool = True
    ) -> None:
        """
        Validate a Spotify ID.

        Parameters
        ----------
        spotify_id : str; positional-only
            Spotify ID.

        enforce_length : bool; keyword-only; default: :code:`True`
            Whether to enforce the canonical 22-character Spotify ID
            length.
        """
        if (
            not isinstance(spotify_id, str)
            or enforce_length
            and len(spotify_id) != 22
            or not spotify_id.isalnum()
        ):
            raise ValueError(f"{spotify_id!r} is not a valid Spotify ID.")

    @staticmethod
    def _validate_spotify_uri(
        spotify_uri: str, /, *, resource_types: set[str]
    ) -> None:
        """
        Validate a Spotify Uniform Resource Identifier (URI).

        Parameters
        ----------
        spotify_uri : str; positional-only
            Spotify URI.

        resource_types : set[str]
            Allowed Spotify resource types.
        """
        if (
            not isinstance(spotify_uri, str)
            or len(uri_parts := spotify_uri.strip().split(":")) != 3
            or uri_parts[0] != "spotify"
            or uri_parts[1] not in resource_types
            or len(spotify_id := uri_parts[2]) != 22
            or not spotify_id.isalnum()
        ):
            raise ValueError(f"{spotify_uri!r} is not a valid Spotify URI.")

    @cached_property
    def available_seed_genres(self) -> set[str]:
        """
        Available seed genres for track recommendations.

        .. admonition:: Third-party application mode
           :class: authorization-scope

           .. tab:: Required

              Extended quota mode before November 27, 2024
                  Access the
                  :code:`GET /recommendations/available-genre-seeds`
                  endpoint. `Learn more. <https://developer.spotify.com
                  /blog/2024-11-27-changes-to-the-web-api>`__

        .. note::

           Accessing this property may call
           :meth:`~minim.api.spotify.GenresAPI.get_seed_genres` and make
           a request to the Spotify Web API.
        """
        return set(self.genres.get_seed_genres()["genres"])

    @cached_property
    def available_markets(self) -> set[str]:
        """
        Markets where Spotify is available.

        .. note::

           Accessing this property may call
           :meth:`~minim.api.spotify.MarketsAPI.get_markets` and make a
           request to the Spotify Web API.
        """
        return set(self.markets.get_markets()["markets"])

    def _resolve_user_identifier(self) -> str:
        """
        Return the Spotify user ID as the user identifier for the
        current account.

        .. note::

           Invoking this method may call
           :meth:`~minim.api.spotify.UsersAPI.get_my_profile` and
           make a request to the Spotify Web API.
        """
        return self.users.get_my_profile()["id"]

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
        method : str; positional-only
            HTTP method.

        endpoint : str; positional-only
            Spotify Web API endpoint.

        retry : bool; keyword-only; default: :code:`True`
            Whether to retry the request if it returns
            :code:`401 Unauthorized` or :code:`429 Too Many Requests`.

        **kwargs : dict[str, Any]
            Keyword arguments to pass to :meth:`httpx.Client.request`.

        Returns
        -------
        response : httpx.Response
            HTTP response.
        """
        if self._expires_at and datetime.now() > self._expires_at:
            self._refresh_access_token()

        resp = self._client.request(method, endpoint, **kwargs)
        status = resp.status_code
        if 200 <= status < 300:
            return resp

        if status == 401 and not self._expires_at and retry:
            self._refresh_access_token()
            return self._request(method, endpoint, retry=False, **kwargs)
        if status == 429 and retry:
            try:
                retry_after = float(resp.headers["Retry-After"]) + 1.0
            except (KeyError, ValueError):
                retry_after = 1.0
            warnings.warn(
                f"Rate limit exceeded. Retrying after {retry_after:.3f} second(s)."
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

    def _require_spotify_premium(self, endpoint_method: str, /) -> None:
        """
        Ensure that a Spotify Premium subscription is active for an
        endpoint method that requires it.

        .. note::

           Invoking this method may call
           :meth:`~minim.api.spotify.UsersAPI.get_my_profile` and
           make a request to the Spotify Web API.

        Parameters
        ----------
        endpoint_method : str; positional-only
            Name of the endpoint method.
        """
        if self._auth_flow == "client_credentials" or (
            (subscription := self.users.get_my_profile().get("product"))
            is not None
            and subscription != "premium"
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
        market : str; positional-only
            ISO 3166-1 alpha-2 country code.
        """
        self._validate_country_code(market)
        if "markets" in self.__dict__ and market not in self.available_markets:
            markets_str = "', '".join(self.available_markets)
            raise ValueError(
                f"{market!r} is not a market in which Spotify is "
                f"available. Valid values: '{markets_str}'."
            )

    def _validate_seed_genre(self, seed_genre: str, /) -> None:
        """
        Validate seed genre.

        Parameters
        ----------
        seed_genre : str; positional-only
            Seed genre.
        """
        if "available_seed_genres" in self.__dict__:
            if seed_genre not in self.available_seed_genres:
                seed_genres_str = "', '".join(
                    sorted(self.available_seed_genres)
                )
                raise ValueError(
                    f"Invalid seed genre {seed_genre!r}. "
                    f"Valid values: '{seed_genres_str}'."
                )
        else:
            self._validate_type("seed_genre", seed_genre, str)

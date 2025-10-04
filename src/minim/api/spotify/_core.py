from collections.abc import Collection
from datetime import datetime
from functools import cached_property
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING, Any
import warnings

from .._shared import OAuth2API
from ._web_api.albums import WebAPIAlbumEndpoints
from ._web_api.artists import WebAPIArtistEndpoints
from ._web_api.audiobooks import WebAPIAudiobookEndpoints
from ._web_api.categories import WebAPICategoryEndpoints
from ._web_api.chapters import WebAPIChapterEndpoints
from ._web_api.episodes import WebAPIEpisodeEndpoints
from ._web_api.genres import WebAPIGenreEndpoints
from ._web_api.markets import WebAPIMarketEndpoints

# from ._web_api.player import WebAPIPlayerEndpoints
from ._web_api.playlists import WebAPIPlaylistEndpoints
from ._web_api.search import WebAPISearchEndpoints
from ._web_api.shows import WebAPIShowEndpoints
from ._web_api.tracks import WebAPITrackEndpoints
from ._web_api.users import WebAPIUserEndpoints

if TYPE_CHECKING:
    import httpx

# TODO: Add hyperlinks to scopes in docstrings.
# TODO: Implement a `raw: bool = False` keyword argument in all
#       endpoints and make the return values more Pythonic.
# TODO: Move the implementations of all aliased endpoints out of the
#       Users section.


class WebAPI(OAuth2API):
    """
    Spotify Web API client.
    """

    _API_NAME = "SpotifyWebAPI"
    _FLOWS = {"auth_code", "pkce", "client_credentials", "implicit"}
    _PROVIDER = "Spotify"
    _ENV_VAR_PREFIX = "SPOTIFY_WEB_API"
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
        persist: bool = True,
        user_identifier: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        flow : str, keyword-only
            Authorization flow.

            .. container::

               **Valid values**:

               * :code:`"auth_code"` — Authorization Code Flow.
               * :code:`"pkce"` — Authorization Code Flow with Proof Key
                 for Code Exchange (PKCE).
               * :code:`"client_credentials"` — Client Credentials Flow.
               * :code:`"implicit"` — Implicit Grant Flow.

        client_id : str, keyword-only, optional
            Client ID. Must be provided unless it is set as system
            environment variable :code:`SPOTIFY_WEB_API_CLIENT_ID` or
            stored in Minim's local token storage.

        client_secret : str, keyword-only, optional
            Client secret. Required for the Authorization Code, Client
            Credentials, and Resource Owner Password Credential flows.
            Must be provided unless it is set as system environment
            variable :code:`SPOTIFY_WEB_API_CLIENT_SECRET` or stored in
            Minim's local token storage.

        redirect_uri : str, keyword-only, optional
            Redirect URI. Required for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            the host is not :code:`127.0.0.1` or :code:`localhost`,
            redirect handling is not available.

        scopes : str or Collection[str], keyword-only, optional
            Authorization scopes the client requests to access user
            resources.

            .. seealso::

               :meth:`get_scopes` — Get a set of scopes to request,
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

               * :code:`None` — Manually paste the redirect URL into
                 the terminal.
               * :code:`"http.server"` — Simple HTTP server.
               * :code:`"playwright"` — Playwright Firefox browser.

        browser : bool, keyword-only, default: :code:`False`
            Specifies whether to automatically open the authorization
            URL in the default web browser for the Authorization Code,
            Authorization Code with PKCE, and Implicit Grant flows. If
            :code:`False`, the authorization URL is printed to the
            terminal.

        persist : bool, keyword-only, default: :code:`True`
            Specifies whether to enable Minim's local token storage for
            this client. If :code:`True`, newly acquired access tokens
            and related information are stored. If :code:`False`, the
            client will not retrieve or store access tokens.

        user_identifier : str, keyword-only, optional
            Unique identifier for the user account to log into for all
            authorization flows but the Client Credentials flow. Used
            when :code:`persist=True` to distinguish between multiple
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

            Prepending the identifier with a plus sign (:code:`"+"`)
            allows authorizing an additional account for the same client
            ID and authorization flow.
        """
        # Initialize subclasses for categorized endpoints
        #: Spotify Web API album endpoints.
        self.albums: WebAPIAlbumEndpoints = WebAPIAlbumEndpoints(self)
        #: Spotify Web API artist endpoints.
        self.artists: WebAPIArtistEndpoints = WebAPIArtistEndpoints(self)
        #: Spotify Web API audiobook endpoints.
        self.audiobooks: WebAPIAudiobookEndpoints = WebAPIAudiobookEndpoints(
            self
        )
        #: Spotify Web API browse category endpoints.
        self.categories: WebAPICategoryEndpoints = WebAPICategoryEndpoints(self)
        #: Spotify Web API audiobook chapter endpoints.
        self.chapters: WebAPIChapterEndpoints = WebAPIChapterEndpoints(self)
        #: Spotify Web API episode endpoints.
        self.episodes: WebAPIEpisodeEndpoints = WebAPIEpisodeEndpoints(self)
        #: Spotify Web API genre endpoints.
        self.genres: WebAPIGenreEndpoints = WebAPIGenreEndpoints(self)
        #: Spotify Web API market endpoints.
        self.markets: WebAPIMarketEndpoints = WebAPIMarketEndpoints(self)
        #: Spotify Web API player endpoints.
        # self.player: WebAPIPlayerEndpoints = WebAPIPlayerEndpoints(self)
        #: Spotify Web API playlist endpoints.
        self.playlists: WebAPIPlaylistEndpoints = WebAPIPlaylistEndpoints(self)
        #: Spotify Web API search endpoints.
        self.search: WebAPISearchEndpoints = WebAPISearchEndpoints(self)
        #: Spotify Web API show endpoints.
        self.shows: WebAPIShowEndpoints = WebAPIShowEndpoints(self)
        #: Spotify Web API track endpoints.
        self.tracks: WebAPITrackEndpoints = WebAPITrackEndpoints(self)
        #: Spotify Web API user endpoints.
        self.users: WebAPIUserEndpoints = WebAPIUserEndpoints(self)

        if flow == "client_credentials" and scopes:
            warnings.warn(
                f"The {self._OAUTH_FLOWS_NAMES['client_credentials']} "
                "in the Spotify Web API does not support scopes."
            )
            scopes = ""

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
            persist=persist,
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

               * :code:`"images"` — Scopes related to custom images,
                 such as :code:`ugc-image-upload`.
               * :code:`"spotify_connect"` — Scopes related to Spotify
                 Connect, such as

                 * :code:`user-read-playback-state`,
                 * :code:`user-modify-playback-state`, and
                 * :code:`user-read-currently-playing`.
               * :code:`"playback"` — Scopes related to playback
                 control, such as :code:`app-remote-control` and
                 :code:`streaming`.
               * :code:`"playlists"` — Scopes related to playlists, such
                 as

                 * :code:`playlist-read-private`,
                 * :code:`playlist-read-collaborative`,
                 * :code:`playlist-modify-private`, and
                 * :code:`playlist-modify-public`.
               * :code:`"follow"` — Scopes related to followed artists
                 and users, such as :code:`user-follow-modify` and
                 :code:`user-follow-read`.
               * :code:`"listening_history"` — Scopes related to
                 playback history, such as

                 * :code:`user-read-playback-position`,
                 * :code:`user-top-read`, and
                 * :code:`user-read-recently-played`.
               * :code:`"library"` — Scopes related to saved content,
                 such as :code:`user-library-modify` and
                 :code:`user-library-read`.
               * :code:`"users"` — Scopes related to user information,
                 such as :code:`user-read-email` and
                 :code:`user-read-private`.
               * :code:`None` for all scopes above.
               * A substring to match in the available scopes.

                 * :code:`"read"` — All scopes above that grant read
                   access, i.e., scopes with :code:`read` in the name.
                 * :code:`"modify"` — All scopes above that grant
                   modify access, i.e., scopes with :code:`modify` in
                   the name.
                 * :code:`"user"` — All scopes above that grant access
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
            Specifies whether to only allow 22-character-long Spotify IDs.

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
            return WebAPI._prepare_spotify_ids(
                spotify_ids.split(","), limit=limit, strict_length=strict_length
            )

        n_ids = len(spotify_ids)
        if n_ids > limit:
            raise ValueError(
                f"A maximum of {limit} Spotify IDs can be sent in one request."
            )
        for idx, id_ in enumerate(spotify_ids):
            spotify_ids[idx] = id_ = id_.strip()
            WebAPI._validate_spotify_id(id_, strict_length=strict_length)
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
            return WebAPI._prepare_spotify_uris(
                spotify_uris.split(","), limit=limit, item_types=item_types
            )

        if len(spotify_uris) > limit:
            raise ValueError(
                f"A maximum of {limit} Spotify URIs can be sent in one request."
            )
        for idx, uri in enumerate(spotify_uris):
            spotify_uris[idx] = uri = uri.strip()
            WebAPI._validate_spotify_uri(uri, item_types=item_types)
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
            Specifies whether to only allow 22-character-long Spotify IDs.
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
        Available seed genres for recommendations.

        .. note::

           Accessing this property for the first time will call
           :meth:`~minim.api.spotify.WebAPIGenreEndpoints.get_available_seed_genres`
           and cache the response for later use.
        """
        return self.genres.get_available_seed_genres()["genres"]

    @cached_property
    def available_markets(self) -> list[str]:
        """
        Markets where Spotify is available.

        .. note::

           Accessing this property for the first time will call
           :meth:`~minim.api.spotify.WebAPIMarketEndpoints.get_available_markets`
           and cache the response for later use.
        """
        return self.markets.get_available_markets()["markets"]

    @cached_property
    def user_profile(self) -> str:
        """
        Current user's profile.
        """
        return self.users.get_user_profile()

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
            Specifies whether to retry the request if the first attempt
            returns a :code:`401 Unauthorized`.

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
            try:
                details = resp.json()["error"]["message"]
            except JSONDecodeError:
                # Fallback for users without access to apps in
                # development mode
                details = resp.text
            raise RuntimeError(f"{status} {resp.reason_phrase}: {details}")
        return resp

    def _resolve_user_identifier(self) -> None:
        """
        Assign the Spotify user ID as the user identifier for the
        current account.
        """
        self._user_identifier = self.user_profile["id"]

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
            _markets = ", ".join(self.available_markets)
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
            _genres = ", ".join(self.available_seed_genres)
            raise ValueError(
                f"Invalid seed genre {seed_genre!r}. Valid values: '{_genres}'."
            )

from collections.abc import Collection
from datetime import datetime
from json.decoder import JSONDecodeError
from typing import TYPE_CHECKING
import warnings

from .._shared import OAuth2API
from ._web_api.albums import WebAPIAlbumEndpoints
from ._web_api.users import WebAPIUserEndpoints

if TYPE_CHECKING:
    import httpx


class WebAPI(OAuth2API):
    """
    Spotify Web API client.
    """

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

        scopes : str or `Collection[str]`, keyword-only, optional
            Authorization scopes the client requests to access user
            resources.

            .. seealso::

               :meth:`get_scopes` — Get a set of scopes to request,
               filtered by categories, patterns, and/or substrings.

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
            a `str`, it must be in ISO 8601 format
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
        matches : str, or `Collection[str]`, optional
            Categories and/or substrings to filter scopes by.

            .. container::

               **Valid values**:

               * :code:`"images"` for scopes related to custom images,
                 such as :code:`ugc-image-upload`.
               * :code:`"spotify_connect"` for scopes related to Spotify
                 Connect, such as

                 * :code:`user-read-playback-state`,
                 * :code:`user-modify-playback-state`, and
                 * :code:`user-read-currently-playing`.
               * :code:`"playback"` for scopes related to playback
                 control, such as :code:`app-remote-control` and
                 :code:`streaming`.
               * :code:`"playlists"` for scopes related to playlists,
                 such as

                 * :code:`playlist-read-private`,
                 * :code:`playlist-read-collaborative`,
                 * :code:`playlist-modify-private`, and
                 * :code:`playlist-modify-public`.
               * :code:`"follow"` for scopes related to followed artists
                 and users, such as :code:`user-follow-modify` and
                 :code:`user-follow-read`.
               * :code:`"listening_history"` for scopes related to
                 playback history, such as

                 * :code:`user-read-playback-position`,
                 * :code:`user-top-read`, and
                 * :code:`user-read-recently-played`.
               * :code:`"library"` for scopes related to saved content,
                 such as :code:`user-library-modify` and
                 :code:`user-library-read`.
               * :code:`"users"` for scopes related to user information,
                 such as :code:`user-read-email` and
                 :code:`user-read-private`.
               * :code:`None` for all scopes above.
               * A substring to match in the possible scopes, such as

                 * :code:`"read"` for all scopes above that grant read
                   access, i.e., scopes with :code:`read` in the name,
                 * :code:`"modify"` for all scopes above that grant
                   modify access, i.e., scopes with :code:`modify` in
                   the name, or
                 * :code:`"user"` for all scopes above that grant access
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

    def _request(
        self, method: str, endpoint: str, retry: bool = True, **kwargs
    ) -> "httpx.Response":
        """
        Make an HTTP request to a Spotify Web API endpoint.

        Parameters
        ----------
        method : str
            HTTP method.

        endpoint : str
            Spotify Web API endpoint.

        **kwargs : dict[str, Any]
            Additional arguments to pass to
            :meth:`httpx.Client.request`.

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
        self._user_identifier = self.users.get_profile()["id"]

from functools import cached_property
import time
from typing import TYPE_CHECKING, Any
import warnings

from ... import __version__, REPOSITORY_URL
from .._shared import OAuth1APIClient

from ._api.database import DatabaseAPI
from ._api.inventory import InventoryAPI
from ._api.marketplace import MarketplaceAPI
from ._api.users import UsersAPI

if TYPE_CHECKING:
    import httpx


class DiscogsAPIClient(OAuth1APIClient):
    """
    Discogs API client.
    """

    _rate_limit_per_second: float

    _ALLOWED_AUTH_FLOWS = {None, "three_legged", "two_legged"}
    _AUTH_FLOWS = {
        None: "possibly unauthenticated client",
        "three_legged": "Three-Legged Flow",
        "two_legged": "Two-Legged Flow",
    }
    _ENV_VAR_PREFIX = "DISCOGS_API"
    _OPTIONAL_AUTH = True
    _PROVIDER = "Discogs"
    _QUAL_NAME = f"minim.api.{_PROVIDER.lower()}.{__qualname__}"
    _SIGNATURE_METHODS = {"PLAINTEXT"}
    BASE_URL = "https://api.discogs.com"
    AUTH_URL = "https://www.discogs.com/oauth/authorize"
    REQUEST_TOKEN_URL = f"{BASE_URL}/oauth/request_token"
    ACCESS_TOKEN_URL = f"{BASE_URL}/oauth/access_token"

    def __init__(
        self,
        *,
        auth_flow: str | None = None,
        consumer_key: str | None = None,
        consumer_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        access_token: str | None = None,
        access_token_secret: str | None = None,
        redirect_handler: str | None = None,
        open_browser: bool = False,
        enable_cache: bool = True,
        limit_rate: bool = True,
        store_tokens: bool = True,
        user_agent: str = f"minim/{__version__} +{REPOSITORY_URL}",
    ) -> None:
        """
        Parameters
        ----------
        auth_flow : str or None; keyword-only
            Authorization flow.

            **Valid values**:

            * :code:`None` – No authentication or authentication using a
              personal access token.
            * :code:`"two_legged"` – Discogs Auth (Two-Legged) Flow.
            * :code:`"three_legged"` – OAuth (Three-Legged) Flow.

        consumer_key : str; keyword-only; optional
            Consumer key. Required for the two-legged and three-legged
            flows unless set as system environment variable
            :code:`DISCOGS_API_CONSUMER_KEY` or stored in the local
            token storage.

        consumer_secret : str; keyword-only; optional
            Consumer secret. Required for the two-legged and
            three-legged flows unless set as system environment
            variable :code:`DISCOGS_API_CONSUMER_SECRET` or stored in
            the local token storage.

        user_identifier : str; keyword-only; optional
            Identifier for the user account. Used when
            :code:`store_tokens=True` to distinguish between multiple
            accounts for the same consumer key and authorization flow.

            If provided, it is used with the consumer key and
            authorization flow to locate a matching stored token. If
            none is found, a new token is obtained and stored under this
            identifier.

            If not provided, the most recently accessed token for the
            consumer key and authorization flow is used. If none exists,
            a new token is obtained and stored using a user identifier
            (e.g., user ID) acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        redirect_uri : str; keyword-only; optional
            Redirect URI (or OAuth callback). Required for the
            three-legged flow.

        access_token : str; keyword-only; optional
            OAuth or personal access token. If provided, the
            authorization process is bypassed.

        access_token_secret : str; positional-only; optional
            OAuth access token secret. Required for the three-legged
            flow when an access token is provided in `access_token`.

        redirect_handler : str or None; keyword-only; optional
            Backend for handling redirects during the authorization
            flow. Redirect handling is only available for hosts
            :code:`localhost`, :code:`127.0.0.1`, or :code:`::1`.

            **Valid values**:

            * :code:`None` – Show authorization URL in and have the
              user manually paste the redirect URL into the terminal.
            * :code:`"http.server"` – Run a HTTP server to intercept
              the redirect after user authorization in any local
              browser.
            * :code:`"playwright"` – Use a Playwright Firefox
              browser to complete the user authorization.

        open_browser : bool; keyword-only; default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the three-legged flow. If
            :code:`False`, the URL is printed to the terminal.

        enable_cache : bool; keyword-only; default: :code:`True`
            Whether to enable an in-memory time-to-live (TTL) cache with
            a least recently used (LRU) eviction policy for this client.
            If :code:`True`, responses from semi-static endpoints are
            cached for one minute to one day, depending on their
            expected update frequency.

            .. seealso::

               :meth:`clear_cache` – Clear specific or all cache entries
               for this client.

        limit_rate : bool; keyword-only; default: :code:`True`
            Whether to enable a token bucket rate limiter for this
            client.

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

        user_agent : str; keyword-only; \
        default: :code:`"minim/x.y.z +https://github.com/bbye98/minim"`
            :code:`User-Agent` value to include in the headers of HTTP
            requests.
        """
        #: Database API endpoints for the Discogs API.
        self.database: DatabaseAPI = DatabaseAPI(self)
        #: Inventory Export and Inventory Upload API endpoints for the
        #: Discogs API.
        self.inventory: InventoryAPI = InventoryAPI(self)
        #: Marketplace API endpoints for the Discogs API.
        self.marketplace: MarketplaceAPI = MarketplaceAPI(self)
        #: User Identity, User Collection, User Wantlist, and User Lists
        #: API endpoints for the Discogs API.
        self.users: UsersAPI = UsersAPI(self)

        self._rate_limit_per_second = 5 / 12 if auth_flow is None else 1
        super().__init__(
            auth_flow=auth_flow,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            signature_method="PLAINTEXT",
            access_token=access_token,
            access_token_secret=access_token_secret,
            redirect_handler=redirect_handler,
            open_browser=open_browser,
            enable_cache=enable_cache,
            limit_rate=limit_rate,
            store_tokens=store_tokens,
            user_agent=user_agent,
        )

    @cached_property
    def _identity(self) -> dict[str, Any]:
        """
        Identity of the current user.
        """
        return self.users.get_my_identity()

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
        Make an HTTP request to a Discogs API endpoint.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

        endpoint : str; positional-only
            Discogs API endpoint.

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
        rate_limiter = self._rate_limiter
        has_rate_limiter = rate_limiter is not None
        if has_rate_limiter:
            rate_limiter.throttle()
        resp = (
            super()._request
            if self._auth_flow == "three_legged"
            else self._client.request
        )(method, endpoint, **kwargs)
        if has_rate_limiter:
            rate_limiter._num_tokens = int(
                resp.headers["x-discogs-ratelimit-remaining"]
            )
        status = resp.status_code
        if 200 <= status < 300:
            return resp

        if status == 429 and retry:
            retry_after = 1 / self._rate_limit_per_second
            warnings.warn(
                "Rate limit exceeded. Retrying after "
                f"{retry_after:.3f} second(s)."
            )
            time.sleep(retry_after)
            return self._request(method, endpoint, retry=False, **kwargs)

        resp_json = resp.json()
        if detail := resp_json.get("detail"):
            detail = detail[0]
            raise RuntimeError(
                f"{status} – {detail['msg']}: {detail['type']} {detail['loc']}"
            )
        else:
            raise RuntimeError(f"{status} – {resp_json['message']}")

    def _require_authentication(self, endpoint_method: str, /) -> None:
        """
        Ensure that the user authentication has been performed for a
        protected endpoint.

        Parameters
        ----------
        endpoint_method : str; positional-only
            Name of the endpoint method.
        """
        if self._auth_flow != "three_legged" and (
            not (auth_header := self._client.headers.get("authorization"))
            or "token" not in auth_header
        ):
            raise RuntimeError(
                f"{self._QUAL_NAME}.{endpoint_method}() requires user "
                "authentication."
            )

    def _resolve_user_identifier(self) -> str:
        """
        Return the Discogs user ID as the user identifier for the
        current account.

        .. note::

           Invoking this method may call
           :meth:`~minim.api.discogs.UsersAPI.get_my_identity` and
           make a request to the Discogs API.
        """
        return self._identity["id"]

    def set_access_token(
        self,
        access_token: str | None = None,
        access_token_secret: str | None = None,
        /,
    ) -> None:
        """
        Set or update the access token and its related metadata.

        .. warning::

           Calling this method replaces all existing values with the
           provided parameters. Parameters not provided explicitly
           will be overwritten by their default values.

        Parameters
        ----------
        access_token : str or None; positional-only; optional
            OAuth or personal access token.

            .. important::

               If the access token was acquired via a different
               authorization flow or client, call :meth:`set_auth_flow`
               first to ensure that all other relevant authorization
               parameters are set correctly.

        access_token_secret : str; positional-only; optional
            OAuth access token secret. Required for the three-legged
            flow when an access token is provided in `access_token`.
        """
        if access_token is None:
            if access_token_secret is not None:
                warnings.warn(
                    "`access_token_secret` is ignored when "
                    "`access_token` is None."
                )

            match self._auth_flow:
                case "two_legged":
                    self._client.headers["authorization"] = (
                        f"Discogs key={self._consumer_key}, "
                        f"secret={self._consumer_secret}"
                    )
                case None | "three_legged":
                    super().set_access_token()
                    if "authorization" in self._client.headers:
                        del self._client.headers["authorization"]
        else:
            match self._auth_flow:
                case None:
                    if access_token_secret is not None:
                        warnings.warn(
                            "`access_token_secret` is ignored when "
                            "`access_token` is a personal access token."
                        )

                    self._client.headers["authorization"] = (
                        f"Discogs token={access_token}"
                    )
                case "two_legged" | "three_legged":
                    super().set_access_token(access_token, access_token_secret)
                    if "authorization" in self._client.headers:
                        del self._client.headers["authorization"]

    def set_auth_flow(
        self,
        auth_flow: str | None,
        /,
        *,
        consumer_key: str | None = None,
        consumer_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        redirect_handler: str | None = None,
        signature_method: str = "PLAINTEXT",
        open_browser: bool = False,
        store_tokens: bool = True,
        authenticate: bool = True,
    ) -> None:
        """
        Set or update the authorization flow and related parameters.

        .. warning::

           Calling this method replaces all existing values with the
           provided parameters. Parameters not provided explicitly
           will be overwritten by their default values.

        Parameters
        ----------
        auth_flow : str or None; keyword-only
            Authorization flow.

            **Valid values**:

            * :code:`None` – No authentication or authentication using a
              personal access token.
            * :code:`"two_legged"` – Discogs Auth (Two-Legged) Flow.
            * :code:`"three_legged"` – OAuth (Three-Legged) Flow.

        consumer_key : str; keyword-only; optional
            Consumer key. Required for the two-legged and three-legged
            flows unless set as system environment variable
            :code:`DISCOGS_API_CONSUMER_KEY` or stored in the local
            token storage.

        consumer_secret : str; keyword-only; optional
            Consumer secret. Required for the two-legged and
            three-legged flows unless set as system environment
            variable :code:`DISCOGS_API_CONSUMER_SECRET` or stored in
            the local token storage.

        user_identifier : str; keyword-only; optional
            Identifier for the user account. Used when
            :code:`store_tokens=True` to distinguish between multiple
            accounts for the same consumer key and authorization flow.

            If provided, it is used with the consumer key and
            authorization flow to locate a matching stored token. If
            none is found, a new token is obtained and stored under this
            identifier.

            If not provided, the most recently accessed token for the
            consumer key and authorization flow is used. If none exists,
            a new token is obtained and stored using a user identifier
            (e.g., user ID) acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        redirect_uri : str; keyword-only; optional
            Redirect URI (or OAuth callback). Required for the
            three-legged flow.

        redirect_handler : str or None; keyword-only; optional
            Backend for handling redirects during the authorization
            flow. Redirect handling is only available for hosts
            :code:`localhost`, :code:`127.0.0.1`, or :code:`::1`.

            **Valid values**:

            * :code:`None` – Show authorization URL in and have the
              user manually paste the redirect URL into the terminal.
            * :code:`"http.server"` – Run a HTTP server to intercept
              the redirect after user authorization in any local
              browser.
            * :code:`"playwright"` – Use a Playwright Firefox
              browser to complete the user authorization.

        signature_method : str; keyword-only; \
        default: :code:`"PLAINTEXT"`
            Mechanism used to sign requests.

            **Valid value**:

            * :code:`"PLAINTEXT"` – Uses the consumer secret and
              the access token secret directly as the signature.

        open_browser : bool; keyword-only; default: :code:`False`
            Whether to automatically open the authorization URL in the
            default web browser for the three-legged flow. If
            :code:`False`, the URL is printed to the terminal.

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

        authenticate : bool; keyword-only; default: :code:`True`
            Whether to immediately initiate the authorization
            flow to acquire an access token.

            .. important::

               Unless :meth:`set_access_token` is called immediately
               after, this should be left as :code:`True` to ensure the
               client's existing token is compatible with the new
               authorization flow.
        """
        self._rate_limit_per_second = 5 / 12 if auth_flow is None else 1
        super().set_auth_flow(
            auth_flow,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            redirect_handler=redirect_handler,
            signature_method=signature_method,
            open_browser=open_browser,
            store_tokens=store_tokens,
            authenticate=authenticate,
        )

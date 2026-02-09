from typing import TYPE_CHECKING, Any

from ... import __version__, REPOSITORY_URL
from .._shared import OAuth1APIClient

from ._api.users import UsersAPI

if TYPE_CHECKING:
    import httpx


class DiscogsAPIClient(OAuth1APIClient):
    """
    Discogs API client.
    """

    _RATE_LIMIT_PER_SECOND: float

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
        redirect_handler: str | None = None,
        open_browser: bool = False,
        enable_cache: bool = True,
        store_tokens: bool = True,
        user_agent: str = f"minim/{__version__} +{REPOSITORY_URL}",
    ) -> None:
        """ """
        #: Users API endpoints for the Discogs API.
        self.users: UsersAPI = UsersAPI(self)

        super().__init__(
            auth_flow=auth_flow,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            user_identifier=user_identifier,
            redirect_uri=redirect_uri,
            signature_method="PLAINTEXT",
            access_token=access_token,
            redirect_handler=redirect_handler,
            open_browser=open_browser,
            enable_cache=enable_cache,
            store_tokens=store_tokens,
            user_agent=user_agent,
        )

        self._RATE_LIMIT_PER_SECOND = 5 / 12 if auth_flow is None else 1

    def _request(
        self, method: str, endpoint: str, /, **kwargs: dict[str, Any]
    ) -> "httpx.Response":
        """ """
        if self._auth_flow == "three_legged":
            resp = super()._request(method, endpoint, **kwargs)
        else:
            resp = self._client.request(method, endpoint, **kwargs)
        return resp

    def _require_authentication(self, endpoint_method: str, /) -> None:
        """
        Ensure that the user authentication has been performed for a
        protected endpoint.

        Parameters
        ----------
        endpoint_method : str; positional-only
            Name of the endpoint method.
        """
        if (
            self._auth_flow != "three_legged"
            and (auth_header := self._client.headers.get("authorization"))
            and "token" not in auth_header
        ):
            raise RuntimeError(
                f"{self._QUAL_NAME}.{endpoint_method}() requires user "
                "authentication."
            )

    def _resolve_user_identifier(self) -> str:
        """ """
        return self.users.get_my_identity()["id"]

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
            Access token.

            .. important::

               If the access token was acquired via a different
               authorization flow or client, call :meth:`set_auth_flow`
               first to ensure that all other relevant authorization
               parameters are set correctly.

        access_token_secret : str; positional-only; optional
            Access token secret.
        """
        if access_token is not None and access_token_secret is None:
            if self._auth_flow == "three_legged":
                raise ValueError(
                    "`access_token_secret` cannot be None when using "
                    f"the {self._AUTH_FLOWS[self._auth_flow]}."
                )

            self._client.headers["authorization"] = (
                f"Discogs token={access_token}"
            )
        else:
            super().set_access_token(access_token, access_token_secret)

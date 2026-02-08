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
    _ENV_VAR_PREFIX = "DISCOGS_API"
    _OPTIONAL_AUTH = True
    _PROVIDER = "Discogs"
    _QUAL_NAME = f"minim.api.{_PROVIDER.lower()}.{__qualname__}"
    BASE_URL = "https://api.discogs.com"
    AUTH_URL = "https://www.discogs.com/oauth/authorize"
    REQUEST_TOKEN_URL = "https://api.discogs.com/oauth/request_token"
    ACCESS_TOKEN_URL = "https://api.discogs.com/oauth/access_token"

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
            return super()._request(method, endpoint, **kwargs)
        else:
            raise NotImplementedError

    def _resolve_user_identifier(self) -> str:
        """ """
        return self.users.get_my_identity()["id"]

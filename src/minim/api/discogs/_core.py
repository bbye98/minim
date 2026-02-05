from ... import __version__
from .._shared import OAuthRedirectHandler, APIClient


class DiscogsAPIClient(APIClient):
    """
    Discogs API client.
    """

    _RATE_LIMIT_PER_SECOND: float

    _ALLOWED_AUTH_FLOWS = {
        None: "unauthenticated client",
        "app_only": "Two-Legged Flow",
        "user_auth": "Three-Legged Flow",
    }
    _ENV_VAR_PREFIX = "DISCOGS_API"
    _PROVIDER = "Discogs"
    _QUAL_NAME = f"minim.api.{_PROVIDER.lower()}.{__qualname__}"
    BASE_URL = "https://api.discogs.com"
    #: Authorization endpoint.
    AUTH_URL = "https://www.discogs.com/oauth/authorize"
    #: Request token endpoint.
    REQUEST_TOKEN_URL = "https://api.discogs.com/oauth/request_token"
    #: Access token endpoint.
    ACCESS_TOKEN_URL = "https://api.discogs.com/oauth/access_token"

    def __init__(
        self,
        *,
        authorization_flow: str | None = None,
        consumer_key: str | None = None,
        consumer_secret: str | None = None,
        user_identifier: str | None = None,
        redirect_uri: str | None = None,
        access_token: str | None = None,
        redirect_handler: str | None = None,
        open_browser: bool = False,
        enable_cache: bool = True,
        store_tokens: bool = True,
        user_agent: str | None = None,
    ) -> None:
        """ """
        super().__init__(
            enable_cache=enable_cache,
            user_agent=user_agent
            or f"minim/{__version__} +https://github.com/bbye98/minim",
        )

        ...

        self._RATE_LIMIT_PER_SECOND = (
            5 / 12 if authorization_flow is None else 1
        )

import base64
from datetime import datetime
import getpass
import hashlib
import json
import os
import re
from typing import Any
from urllib.parse import quote

import httpx
from playwright.sync_api import sync_playwright

from .._shared import APIClient, TokenDatabase
from ._api.tracks import TracksAPI
from ._api.users import UsersAPI


class PrivateQobuzAPI(APIClient):
    """ """

    _ALLOWED_AUTH_FLOWS = {None, "password"}
    _AUTH_FLOWS = {
        None: "unauthenticated client",
        "password": "Qobuz Web Player login flow",
    }
    _ENV_VAR_PREFIX = "PRIVATE_QOBUZ_API"
    _PROVIDER = "Qobuz"
    _QUAL_NAME = f"minim.api.{_PROVIDER.lower()}.{__qualname__}"
    _VERSION = "1.17"
    BASE_URL = "https://www.qobuz.com/api.json/0.2"

    def __init__(
        self,
        *,
        authorization_flow: str | None,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_identifier: str | None = None,
        access_token: str | None = None,
        credential_handler: str | None = None,
        enable_cache: bool = True,
        store_tokens: bool = True,
        **kwargs: dict[str, Any],
    ) -> None:
        """ """
        super().__init__(enable_cache=enable_cache)

        # Initialize subclasses for endpoint groups
        #: Tracks API endpoints for the private Qobuz API.
        self.tracks: TracksAPI = TracksAPI(self)
        #: Users API endpoints for the private Qobuz API.
        self.users: UsersAPI = UsersAPI(self)

        # If an app ID is not provided, try to retrieve it and its
        # corresponding app secret from environment variables
        if client_id is None or client_secret is None:
            client_id = os.environ.get(f"{self._ENV_VAR_PREFIX}_CLIENT_ID")
            client_secret = os.environ.get(
                f"{self._ENV_VAR_PREFIX}_CLIENT_SECRET"
            )

        # If the app ID is still missing, get it from Qobuz
        if client_id is None:
            client_id, client_secret = self._resolve_app_credentials()

        if authorization_flow is not None:
            if user_identifier and user_identifier[0] == "~":
                user_identifier = user_identifier[1:]
            elif store_tokens and (
                account := TokenDatabase._get_token(
                    self.__class__.__name__,
                    authorization_flow=authorization_flow,
                    client_id=client_id,
                    user_identifier=user_identifier,
                )
            ):
                # If an access token is not provided, try to retrieve it
                # from local token storage
                access_token = account["access_token"]
                client_secret = account["client_secret"]
                self._token_extras = (
                    json.loads(token_extras)
                    if isinstance(token_extras := account["extras"], str)
                    else token_extras
                )

        self.set_authorization_flow(
            authorization_flow,
            client_id=client_id,
            client_secret=client_secret,
            user_identifier=user_identifier,
            credential_handler=credential_handler,
            store_tokens=store_tokens,
            authenticate=False,
        )
        if authorization_flow is not None:
            if access_token:
                self.set_access_token(access_token)
            else:
                self._obtain_access_token(**kwargs)

    @classmethod
    def get_tokens(
        cls,
        *,
        authorization_flows: str | list[str] | None = None,
        client_ids: str | list[str] | None = None,
        user_identifiers: str | list[str] | None = None,
    ) -> None:
        """
        Retrieve specific or all user authentication tokens and their
        metadata for this client from local storage.

        Parameters
        ----------
        authorization_flows : str or list[str]; keyword-only; optional
            Authorization flows.

        client_ids : str or list[str]; keyword-only; optional
            Client IDs.

        user_identifiers : str or list[str]; keyword-only; optional
            Identifiers for the user accounts.
        """
        TokenDatabase.get_tokens(
            client_names=cls.__name__,
            authorization_flows=authorization_flows,
            client_ids=client_ids,
            user_identifiers=user_identifiers,
        )

    @classmethod
    def remove_tokens(
        cls,
        *,
        authorization_flows: str | list[str] | None = None,
        client_ids: str | list[str] | None = None,
        user_identifiers: str | list[str] | None = None,
    ) -> None:
        """
        Remove specific or all user authentication tokens and their
        metadata for this client from local storage.

        .. warning::

           If none of `authorization_flows`, `client_ids`, or
           `user_identifiers` are provided, all tokens for this client
           will be removed from local storage.

        Parameters
        ----------
        authorization_flows : str or list[str]; keyword-only; optional
            Authorization flows.

        client_ids : str or list[str]; keyword-only; optional
            Client IDs.

        user_identifiers : str or list[str]; keyword-only; optional
            Identifiers for the user accounts.
        """
        TokenDatabase.remove_tokens(
            client_names=cls.__name__,
            authorization_flows=authorization_flows,
            client_ids=client_ids,
            user_identifiers=user_identifiers,
        )

    @staticmethod
    def _resolve_app_credentials() -> tuple[str, list[str]]:
        """
        Resolve the app ID and secret using the Qobuz Web Player login
        page.

        Returns
        -------
        app_id : str
            App ID.

        app_secrets : list[str]
            Possible app secrets.
        """
        with httpx.Client(
            base_url="https://play.qobuz.com", follow_redirects=True
        ) as client:
            bundle = client.get(
                re.search(
                    "/resources/.*/bundle.js", client.get("login").text
                ).group(0)  # /resources/8.1.0-b019/bundle.js
            ).text
        return (
            re.search(
                '(?:production:{api:{appId:")(.*?)(?:",appSecret)', bundle
            ).group(1),
            [
                base64.b64decode(
                    "".join((secret, *match.groups()))[:-44]
                ).decode()
                for secret, match in (
                    (
                        secret,
                        re.search(
                            f'(?:{city.capitalize()}",info:")(.*?)(?:",extras:")'
                            '(.*?)(?:"},{offset)',
                            bundle,
                        ),
                    )
                    for secret, city in re.findall(
                        r'(?:[a-z].initialSeed\(")(.*?)'
                        r'(?:",window.utimezone.)(.*?)\)',
                        bundle,
                    )
                )
                if match
            ],
        )

    def set_access_token(self, access_token: str | None, /) -> None:
        """
        Set or update the user authentication token.

        Parameters
        ----------
        access_token : str or None; positional-only
            User authentication token.
        """
        if access_token is None:
            if self._auth_flow is not None:
                raise ValueError(
                    "`access_token` cannot be None when using the "
                    f"{self._AUTH_FLOWS[self._auth_flow]}."
                )
            if "X-User-Auth-Token" in self._client.headers:
                del self._client.headers["X-User-Auth-Token"]
            return

        self._client.headers["X-User-Auth-Token"] = access_token

    def set_authorization_flow(
        self,
        authorization_flow: str | None,
        /,
        *,
        client_id: str,
        client_secret: str | None = None,
        user_identifier: str | None = None,
        credential_handler: str | None = None,
        store_tokens: bool = True,
        authenticate: bool = True,
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Set or update the authorization flow and related parameters.

        .. warning::

           Calling this method replaces all existing values with the
           provided parameters. Parameters not provided explicitly
           will be overwritten by their default values.

        Parameters
        ----------
        authorization_flow : str or None; keyword-only
            Authorization flow.

            **Valid values**:

            .. container::

               * :code:`None` – No authentication.
               * :code:`"password"` – Qobuz Web Player login flow.

        client_id : str; keyword-only; optional
            Application ID. If not provided, it is loaded from the
            system environment variable :code:`QOBUZ_API_CLIENT_ID`
            or from the local token storage if available, or retrieved
            from the Qobuz Web Player login page otherwise.

        client_secret : str; keyword-only; optional
            Application secret. If not provided, it is loaded from the
            system environment variable :code:`QOBUZ_API_CLIENT_SECRET`
            or from the local token storage if available, or retrieved
            from the Qobuz Web Player login page otherwise.

        user_identifier : str; keyword-only; optional
            Identifier for the user account. Used when
            :code:`store_tokens=True` to distinguish between multiple
            accounts for the same client ID and authorization flow.

            If provided, it is used with the client ID and authorization
            flow to locate a matching stored token. If none is found, a
            new token is obtained and stored under this identifier.

            If not provided, the most recently accessed token for the
            client ID and authorization flow is used. If none exists, a
            new token is obtained and stored using a user identifier
            (e.g., user ID) acquired from a successful authorization.

            Prefixing the identifier with a tilde (:code:`~`) bypasses
            token retrieval, forces reauthorization, and stores the new
            token under the suffix.

        credential_handler : str; keyword-only; optional
            Backend for handling user credentials during the Qobuz Web
            Player login flow. If not specified, the client first looks
            for credentials in `kwargs` and falls back to prompting for
            them in an echo-free terminal.

            **Valid values**:

            .. container::

               * :code:`"kwargs"` – Use credentials provided directly
                 via the `username` and `password` keyword arguments.
               * :code:`"getpass"` – Prompt for credentials in an
                 echo-free terminal.
               * :code:`"playwright"` – Open the Qobuz Web Player login
                 page in a Playwright Firefox browser.

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
            flow to acquire an user authentication token.

            .. important::

               Unless :meth:`set_access_token` is called immediately
               after, this should be left as :code:`True` to ensure the
               client's existing token is compatible with the new
               authorization flow.

        **kwargs : dict[str, Any]
            Keyword arguments to pass to the internal method that
            obtains user authentication tokens.
        """
        if authorization_flow not in self._ALLOWED_AUTH_FLOWS:
            flows_str = "', '".join(
                sorted(f for f in self._ALLOWED_AUTH_FLOWS if f)
            )
            raise ValueError(
                f"Invalid authorization flow {authorization_flow!r}. "
                f"Valid values: '{flows_str}'."
            )
        self._auth_flow = authorization_flow
        self._client.headers["X-App-Id"] = self._client_id = client_id
        self._client_secret = client_secret
        self._user_identifier = user_identifier
        self._credential_handler = credential_handler
        self._store_tokens = store_tokens

        if authenticate and authorization_flow is not None:
            self._obtain_access_token(**kwargs)

    def _login(
        self, username: str | None = None, password: str | None = None
    ) -> dict[str, Any]:
        """ """
        if self._credential_handler == "playwright":
            with sync_playwright() as playwright:
                browser = playwright.firefox.launch(headless=False)
                context = browser.new_context(
                    color_scheme="dark",
                    locale="en-US",
                    timezone_id="America/Los_Angeles",
                    **playwright.devices["Desktop Firefox HiDPI"],
                )
                page = context.new_page()
                with page.expect_request(
                    f"{self.BASE_URL}/oauth/callback*", timeout=0
                ) as callback:
                    page.goto("https://play.qobuz.com/login")
                resp_json = callback.value.response().json()
                context.close()
                browser.close()
            return resp_json

        if self._credential_handler in {None, "kwargs"}:
            return

        # self._credential_handler in {None, "getpass"}
        return

    def _obtain_access_token(
        self, authorization_flow: str | None = None, **kwargs: dict[str, Any]
    ) -> None:
        """ """
        if not authorization_flow:
            authorization_flow = self._auth_flow

        if authorization_flow is None:
            self.set_access_token(None)

        # authorization_flow == "password"
        resp_json = self._login(**kwargs)
        user_auth_token = resp_json.pop("token")
        self.set_access_token(user_auth_token)
        self._token_extras = resp_json
        if self._user_identifier is None and self._auth_flow is not None:
            self._user_identifier = self._resolve_user_identifier()

        # Figure out the working application secret from the possible
        # values
        if isinstance(self._client_secret, list):
            for client_secret in self._client_secret:
                try:
                    self._client_secret = client_secret
                    self.tracks.get_track_playback_info(344521217, format_id=5)
                    break
                except RuntimeError:
                    continue
            else:
                raise RuntimeError(
                    "No valid application secret was found in 'bundle.js'."
                )

        if self._store_tokens:
            TokenDatabase.add_token(
                self.__class__.__name__,
                authorization_flow=self._auth_flow,
                client_id=self._client_id,
                client_secret=self._client_secret,
                user_identifier=self._user_identifier,
                redirect_uri=None,
                scopes="",
                token_type=None,
                access_token=user_auth_token,
                refresh_token=None,
                expires_at=None,
                extras=resp_json,
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        /,
        *,
        signed: bool = False,
        **kwargs: dict[str, Any],
    ) -> "httpx.Response":
        """
        Make an HTTP request to a private Qobuz API endpoint.

        Parameters
        ----------
        method : str; positional-only
            HTTP method.

        endpoint : str; positional-only
            Private Qobuz API endpoint.

        signed : bool; keyword-only; default: :code:`False`
            ...

        **kwargs : dict[str, Any]
            Keyword parameters to pass to :meth:`httpx.Client.request`.

        Returns
        -------
        response : httpx.Response
            HTTP response.
        """
        if signed:
            timestamp = datetime.now().timestamp()
            params_str = "".join(
                f"{k}{v}" for k, v in sorted(kwargs["params"].items())
            )
            kwargs["params"] |= {
                "request_ts": timestamp,
                "request_sig": hashlib.md5(
                    (
                        f"{endpoint.replace('/', '')}{params_str}"
                        f"{timestamp}{self._client_secret}"
                    ).encode()
                ).hexdigest(),
            }
        resp = self._client.request(method, endpoint, **kwargs)
        status = resp.status_code
        if 200 <= status < 300:
            return resp

        raise RuntimeError(
            f"{status} {resp.reason_phrase} – {resp.json()['message']}"
        )

    def _require_authentication(self, endpoint_method: str, /) -> None:
        """
        Ensure that the user authentication has been performed for a
        protected endpoint.

        Parameters
        ----------
        endpoint_method : str; positional-only
            Name of the endpoint method.
        """
        if self._auth_flow is None:
            raise RuntimeError(
                f"{self._QUAL_NAME}.{endpoint_method}() requires user "
                "authentication."
            )

    def _resolve_user_identifier(self) -> str:
        """
        Return the Qobuz user ID as the user identifier for the
        current account.

        .. note::

           Invoking this method may call
           :meth:`~minim.api.tidal.UsersAPI.get_my_profile` and
           make a request to the TIDAL API.
        """
        return self._token_extras.get("user_id") or self.users.get_my_profile()

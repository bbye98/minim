from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import WebAPI


class UserEndpoints:
    """
    Spotify Web API user endpoints.
    """

    def __init__(self, client: "WebAPI") -> None:
        """
        Parameters
        ----------
        client : `WebAPI`
            ...
        """
        self._client = client

    def get_me(self) -> dict[str, Any]:
        """
        ...
        """
        self._client._require_scope(
            "get_me", {"user-read-private", "user-read-email"}
        )
        return self._client._request("get", "me").json()

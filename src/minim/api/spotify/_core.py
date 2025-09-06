from collections.abc import Collection
import fnmatch

from .._shared import _OAuth2API


class WebAPI(_OAuth2API):
    """ """

    _FLOWS = {"auth_code", "pkce", "client_credentials", "implicit"}
    _PROVIDER = "Spotify"
    AUTH_URL = "https://accounts.spotify.com/authorize"
    BASE_URL = "https://api.spotify.com/v1"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    SCOPES = {
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

    @classmethod
    def get_scopes(
        cls, categories: str | Collection[str] | None = None
    ) -> set[str]:
        """ """
        # Return all scopes if no categories are provided
        if categories is None:
            return set().union(*cls.SCOPES.values())

        if isinstance(categories, str):
            # Return scopes for a specific category
            if categories in cls.SCOPES:
                return cls.SCOPES[categories]

            # Return scopes matching a pattern
            if any(char in categories for char in "*?["):
                return {
                    scope
                    for scopes in cls.SCOPES.values()
                    for scope in fnmatch.filter(scopes, categories)
                }

            # Return scopes containing a substring
            return {
                scope
                for scopes in cls.SCOPES.values()
                for scope in scopes
                if categories in scope
            }

        # Recursively gather scopes for multiple
        # categories/patterns/substrings
        return {
            scope
            for category in categories
            for scope in cls.get_scopes(category)
        }

from typing import TYPE_CHECKING

from ..._shared import ResourceAPI

if TYPE_CHECKING:
    from .. import PrivateQobuzAPI


class PrivateQobuzResourceAPI(ResourceAPI):
    """
    Abstract base class for Qobuz API resource endpoint groups.
    """

    _RELATIONSHIPS: set[str]
    _client: "PrivateQobuzAPI"

    @classmethod
    def _prepare_expand(
        cls,
        expand: str | list[str],
        /,
        *,
        relationships: set[str] | None = None,
    ) -> str:
        """
        Normalize, validate, and serialize related resources.

        Parameters
        ----------
        expand : str | list[str]; positional-only
            Related resources to include metadata for in the response.

        resources : set[str]; keyword-only; optional
            Valid related resources. If not specified,
            :code:`cls._RELATIONSHIPS` is used.

        Returns
        -------
        expand : str
            Comma-separated string of related resources to include
            metadata for.
        """
        if relationships is None:
            relationships = getattr(cls, "_RELATIONSHIPS", {})
        if isinstance(expand, str):
            return cls._prepare_expand(expand.split(","))
        if not isinstance(expand, tuple | list | set):
            raise ValueError("`expand` must be a string or a list of strings.")
        for resource in expand:
            if resource not in relationships:
                relationships_str = "', '".join(sorted(relationships))
                raise ValueError(
                    f"Invalid related resource {resource!r}. "
                    f"Valid values: '{relationships_str}'."
                )
        return ",".join(expand)

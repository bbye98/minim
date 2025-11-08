from collections.abc import Collection

from ..._shared import ResourceAPI


class TIDALResourceAPI(ResourceAPI):
    """
    Abstract base class for TIDAL API resource endpoint groups.
    """

    _RESOURCES: set[str]

    def _prepare_include(self, include: Collection[str], /) -> Collection[str]:
        """
        Prepare a collection of related resources to include in the
        response.

        Parameters
        ----------
        includes : Collection[str], positional-only
            Related resources to include in the response.
        """
        if isinstance(include, str):
            include = [include]
        for resource in include:
            if resource not in self._RESOURCES:
                _resources = "', '".join(sorted(self._RESOURCES))
                raise ValueError(
                    f"Invalid related resource {resource!r}. "
                    f"Valid values: '{_resources}'."
                )
        return include

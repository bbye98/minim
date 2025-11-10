from collections.abc import Collection

from ..._shared import ResourceAPI


class TIDALResourceAPI(ResourceAPI):
    """
    Abstract base class for TIDAL API resource endpoint groups.
    """

    _RESOURCES: set[str]

    def _prepare_include(
        self, include: Collection[str], /, *, resources: set[str] | None = None
    ) -> Collection[str]:
        """
        Prepare a collection of related resources to include in the
        response.

        Parameters
        ----------
        includes : Collection[str], positional-only
            Related resources to include in the response.

        resources : set[str], keyword-only, optional
            Valid resources. If not provided, :code:`self._RESOURCES` is
            used.
        """
        if resources is None:
            resources = self._RESOURCES
        if isinstance(include, str):
            include = [include]
        elif not isinstance(include, Collection):
            raise ValueError(
                "`include` must be a string or a collection of strings."
            )
        for resource in include:
            if resource not in resources:
                _resources = "', '".join(sorted(resources))
                raise ValueError(
                    f"Invalid related resource {resource!r}. "
                    f"Valid values: '{_resources}'."
                )
        return include

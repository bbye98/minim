from __future__ import annotations
from typing import TYPE_CHECKING

from ..._shared import TTLCache
from ._shared import TIDALResourceAPI

if TYPE_CHECKING:
    from typing import Any

    from ...._types import Collection


class RulesAPI(TIDALResourceAPI):
    """
    Usage Rules API endpoints for the TIDAL API.

    .. important::

       This class is managed by :class:`~minim.api.tidal.TIDALAPIClient`
       and should not be instantiated directly.
    """

    @TTLCache.cached_method(ttl="static")
    def get_usage_rules(
        self, rule_ids: str | Collection[str], /
    ) -> dict[str, Any]:
        """
        `Usage Rules > Get Single Usage Rule
        <https://tidal-music.github.io/tidal-api-reference/#/usageRules
        /get_usageRules__id_>`_: Get TIDAL catalog information for a
        usage rule․
        `Usage Rules > Get Multiple Usage Rules
        <https://tidal-music.github.io/tidal-api-reference/#/usageRules
        /get_usageRules>`_: Get TIDAL catalog information for multiple
        usage rules.

        Parameters
        ----------
        rule_ids : str or Collection[str]; positional-only
            TIDAL IDs of the usage rules.

            **Examples**: :code:`"hkgYE3k5zqU2lmFo8CZbHKdf"`,
            :code:`["hkgYE3k5zqU2lmFo8CZbHKdf", "VFJBQ0tTOjEyMzpOTw"]`.

        Returns
        -------
        usage_rules : dict[str, Any]
            TIDAL metadata for the usage rules.

            .. admonition:: Sample responses
               :class: response dropdown

               .. tab-set::

                  .. tab-item:: Single usage rule

                     .. code-block::

                        ...

                  .. tab-item:: Multiple usage rules

                     .. code-block::

                        ...
        """
        return self._get_resources(
            "usageRules", rule_ids, resource_identifier_type="rule_ids"
        )

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
        expand : str or list[str]; positional-only
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
            return cls._prepare_expand(expand.strip().split(","))
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

    @staticmethod
    def _prepare_album_ids(album_ids: str | list[str], /) -> str:
        """
        Normalize, validate, and serialize Qobuz album IDs.

        Parameters
        ----------
        album_ids : str or list[str]; positional-only
            Qobuz IDs of the albums.

        Returns
        -------
        album_ids : str
            Comma-separated string of album IDs.
        """
        if isinstance(album_ids, str):
            return PrivateQobuzResourceAPI._prepare_album_ids(
                album_ids.strip().split(",")
            )
        if not isinstance(album_ids, tuple | list | set):
            raise TypeError(
                "Qobuz album IDs must be provided as integers, "
                "strings, or lists of integers and/or strings."
            )
        for album_id in album_ids:
            PrivateQobuzResourceAPI._validate_album_id(album_id)
        return ",".join(album_ids)

    @staticmethod
    def _prepare_comma_separated_values(
        parameter: str, values: str | list[str], /, allowed_values: set[str]
    ) -> str:
        """
        Normalize, validate, and serialize comma-separated values.

        Parameters
        ----------
        parameter : str; positional-only
            Name of the parameter being prepared.

        values : str or list[str]; positional-only
            Comma-separated values.

        allowed_values : set[str]; positional-only
            Allowed values for the parameter.

        Returns
        -------
        values : str
            Comma-separated string of values.
        """
        if isinstance(values, str):
            values = values.strip().split(",")
        for value in values:
            if value not in allowed_values:
                allowed_values_str = "', '".join(allowed_values)
                raise ValueError(
                    f"Invalid {parameter} {value!r}. "
                    f"Valid values: '{allowed_values_str}'."
                )
        return ",".join(values)

    @staticmethod
    def _prepare_qobuz_ids(
        qobuz_ids: int | str | list[int | str], /, *, data_type: type
    ) -> list[int]:
        """
        Normalize, validate, and serialize or prepare a list of Qobuz
        IDs.

        Parameters
        ----------
        qobuz_ids : int, str, or list[int | str]; positional-only
            Qobuz IDs.

        data_type : type; keyword-only
            Data type of the return value.

            **Valid values**: :code:`str`, :code:`list`,
            :code:`dict` (only for tracks).

        Returns
        -------
        qobuz_ids : str
            Comma-separated string or list of Qobuz IDs.
        """
        if isinstance(qobuz_ids, str):
            return PrivateQobuzResourceAPI._prepare_qobuz_ids(
                qobuz_ids.split(","), data_type=data_type
            )
        if data_type is str:
            if isinstance(qobuz_ids, int):
                return str(qobuz_ids)
            PrivateQobuzResourceAPI._validate_qobuz_ids(qobuz_ids)
            return ",".join(str(qobuz_id) for qobuz_id in qobuz_ids)
        elif data_type is list:
            if isinstance(qobuz_ids, int):
                return [qobuz_ids]
            PrivateQobuzResourceAPI._validate_qobuz_ids(qobuz_ids)
            return [int(qobuz_id) for qobuz_id in qobuz_ids]
        else:
            if isinstance(qobuz_ids, int):
                return [{"track_id": qobuz_ids}]
            PrivateQobuzResourceAPI._validate_qobuz_ids(qobuz_ids)
            return [{"track_id": qobuz_id} for qobuz_id in qobuz_ids]

    @staticmethod
    def _validate_album_id(album_id: str, /) -> None:
        """
        Validate a Qobuz album ID.

        Parameters
        ----------
        album_id : str; positional-only
            Qobuz album ID.
        """
        if not isinstance(album_id, str):
            raise TypeError("Qobuz album IDs must be strings.")
        if not album_id.isalnum():
            raise ValueError(
                f"Qobuz album ID {album_id!r} is not alphanumeric."
            )

    # def _validate_genre_id(self, genre_id: int | str, /) -> None:
    #     """
    #     Validate genre ID.

    #     Parameters
    #     ----------
    #     genre_id : str; positional-only
    #         Genre ID.
    #     """
    #     try:
    #         genre_id = int(genre_id)
    #     except TypeError:
    #         raise TypeError(
    #             "Qobuz genre IDs must be integers or their string "
    #             "representations."
    #         )
    #     if "available_genres" in self._client.__dict__:
    #         if genre_id not in self._client.available_genres:
    #             raise ValueError(
    #                 f"Invalid genre ID {genre_id!r}. Valid values are "
    #                 "the keys of the `available_genres` property in the "
    #                 "private Qobuz API client instance."
    #             )

    @staticmethod
    def _validate_qobuz_ids(
        qobuz_ids: int | str | list[int | str], /, *, _recursive: bool = True
    ) -> None:
        """
        Validate one or more Qobuz IDs.

        Parameters
        ----------
        qobuz_ids : int, str, or list[int | str]; positional-only
            Qobuz IDs.
        """
        if not isinstance(qobuz_ids, int) and not qobuz_ids:
            raise ValueError("At least one Qobuz ID must be specified.")

        if isinstance(qobuz_ids, str):
            if _recursive:
                PrivateQobuzResourceAPI._validate_qobuz_ids(
                    qobuz_ids.split(",")
                )
            elif not qobuz_ids.isdecimal():
                raise ValueError(f"Invalid Qobuz ID {qobuz_ids!r}.")
        elif not isinstance(qobuz_ids, int):
            if _recursive:
                if not isinstance(qobuz_ids, tuple | list | str):
                    raise TypeError(
                        "Qobuz IDs must be provided as integers, "
                        "strings, or lists of integers and/or strings."
                    )
                for qobuz_id in qobuz_ids:
                    PrivateQobuzResourceAPI._validate_qobuz_ids(
                        qobuz_id, _recursive=False
                    )
            else:
                raise ValueError(f"Invalid Qobuz ID {qobuz_ids!r}.")

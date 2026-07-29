from __future__ import annotations

TAG_VERSIONS = {(2, 2, 0), (2, 3, 0), (2, 4, 0)}


def normalize_id3v1_tag_version(
    tag_version: str | tuple[int, int], /
) -> tuple[int, int]:
    """
    Normalize ID3v1 tag version.

    Parameters
    ----------
    tag_version : str or tuple[int, int]; default: :code:`(1, 1)`
        ID3v1 tag version.

        **Valid values**: :code:`"1.0"` or :code:`(1, 0)`,
        :code:`"1.1"` or :code:`(1, 1)`.

    Returns
    -------
    tag_version : tuple[int, int]
        ID3v1 tag version.
    """
    match tag_version:
        case tuple() | list():
            return tag_version
        case str():
            return tuple(int(v) for v in tag_version.split("."))
        case _:
            raise TypeError(
                "`tag_version` must be a string or a tuple of two integers."
            )


def normalize_id3v2_tag_version(
    tag_version: str | tuple[int, int, int], /
) -> tuple[int, int, int]:
    """
    Normalize ID3v2 tag version.

    Parameters
    ----------
    tag_version : str or tuple[int, int, int]
        ID3v2 tag version.

        **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
        :code:`"2.3.0"` or :code:`(2, 3, 0)`,
        :code:`"2.4.0"` or :code:`(2, 4, 0)`.

    Returns
    -------
    tag_version : tuple[int, int, int]
        ID3v2 tag version.
    """
    match tag_version:
        case tuple() | list():
            return tag_version
        case str():
            return tuple(int(v) for v in tag_version.split("."))
        case _:
            raise TypeError(
                "`tag_version` must be a string or a tuple of three integers."
            )

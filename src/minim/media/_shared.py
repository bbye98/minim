import mmap


def as_buffer(
    stream: bytes | bytearray | memoryview | mmap.mmap,
) -> memoryview:
    """
    Return a C-level buffer interface to a bytes-like object.

    Parameters
    ----------
    bytestream : bytes, bytearray, memoryview, or mmap.mmap; \
    positional-only; optional
        Bytes-like object.

    Returns
    -------
    view : memoryview
        Buffer interface to the bytes-like object.
    """
    match stream:
        case bytes() | bytearray() | mmap.mmap():
            stream = memoryview(stream)
        case memoryview():
            pass
        case _:
            raise TypeError("`stream` must be a bytes-like object.")
    return stream

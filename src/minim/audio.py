"""
Audio file objects
==================
.. moduleauthor:: Benjamin Ye <GitHub: bbye98>

This module provides convenient Python objects to keep track of audio
file handles and metadata, and convert between different audio formats.
"""

import base64
import datetime
from importlib.util import find_spec
from io import BytesIO
import logging
import pathlib
import re
import subprocess
from typing import Any, Union
import urllib
import warnings

from mutagen import id3, flac, mp3, mp4, oggflac, oggopus, oggvorbis, wave

from . import utility, FOUND_FFMPEG
from .qobuz import _parse_performers

if FOUND_FFMPEG:
    from . import FFMPEG_CODECS
if (FOUND_PILLOW := find_spec("PIL") is not None):
    from PIL import Image

__all__ = ["Audio", "FLACAudio", "MP3Audio", "MP4Audio", "OggAudio", "WAVEAudio"]


class _ID3:
    """
    ID3 metadata container handler for MP3 and WAVE audio files.

    .. attention::

       This class should *not* be instantiated manually. Instead, use
       :class:`MP3Audio` or :class:`WAVEAudio` to process metadata for
       MP3 and WAVE audio files, respectively.

    Parameters
    ----------
    filename : `str`
        Audio filename.

    tags : `mutagen.id3.ID3`
        ID3 metadata.
    """

    _FIELDS = {
        # field: (ID3 frame, base class, typecasting function)
        "album": ("TALB", "text", None),
        "album_artist": ("TPE2", "text", None),
        "artist": ("TPE1", "text", None),
        "comment": ("COMM", "text", None),
        "compilation": ("TCMP", "text", lambda x: str(int(x))),
        "composer": ("TCOM", "text", None),
        "copyright": ("TCOP", "text", None),
        "date": ("TDRC", "text", None),
        "genre": ("TCON", "text", None),
        "isrc": ("TSRC", "text", None),
        "lyrics": ("USLT", "text", None),
        "tempo": ("TBPM", "text", str),
        "title": ("TIT2", "text", None),
    }

    def __init__(self, filename: str, tags: id3.ID3) -> None:
        """
        Create an ID3 tag handler.
        """

        self._filename = filename
        self._tags = tags
        self._from_file()

    def _from_file(self) -> None:
        """
        Get metadata from the ID3 tags embedded in the audio file.
        """

        for field, (frame, base, _) in self._FIELDS.items():
            value = self._tags.getall(frame)
            if value:
                value = (
                    [sv for v in value for sv in getattr(v, base)]
                    if len(value) > 1
                    else getattr(value[0], base)
                )
                if list not in self._FIELDS_TYPES[field]:
                    value = utility.format_multivalue(value, False, primary=True)
                    if not isinstance(value, self._FIELDS_TYPES[field]):
                        try:
                            value = self._FIELDS_TYPES[field][0](value)
                        except ValueError:
                            logging.warning()
                            continue
                else:
                    if not isinstance(value[0], self._FIELDS_TYPES[field]):
                        try:
                            value = [self._FIELDS_TYPES[field][0](v) for v in value]
                        except ValueError:
                            continue
                    if len(value) == 1:
                        value = value[0]
            else:
                value = None
            setattr(self, field, value)

        if "TPOS" in self._tags:
            disc_number = getattr(self._tags.get("TPOS"), "text")[0]
            if "/" in disc_number:
                self.disc_number, self.disc_count = (
                    int(d) for d in disc_number.split("/")
                )
            else:
                self.disc_number = int(disc_number)
                self.disc_count = None
        else:
            self.disc_number = self.disc_count = None

        if "TRCK" in self._tags:
            track_number = getattr(self._tags.get("TRCK"), "text")[0]
            if "/" in track_number:
                self.track_number, self.track_count = (
                    int(t) for t in track_number.split("/")
                )
            else:
                self.track_number = int(track_number)
                self.track_count = None
        else:
            self.track_number = self.track_count = None

        artwork = self._tags.getall("APIC")
        if artwork:
            self.artwork = artwork[0]
            if self.artwork.type != 3 and len(artwork) > 1:
                for p in artwork:
                    if p.type == 3:
                        self.artwork = p
                        break
            self._artwork_format = self.artwork.mime.split("/")[1]
            self.artwork = self.artwork.data
        else:
            self.artwork = self._artwork_format = None

    def write_metadata(self) -> None:
        """
        Write metadata to file.
        """

        for field, (frame, base, func) in self._FIELDS.items():
            value = getattr(self, field)
            if value:
                value = utility.format_multivalue(
                    value, self._multivalue, sep=self._sep
                )
                self._tags.add(
                    getattr(id3, frame)(**{base: func(value) if func else value})
                )

        if "TXXX:comment" in self._tags:
            self._tags.delall("TXXX:comment")

        if disc_number := getattr(self, "disc_number", None):
            disc = str(disc_number)
            if disc_count := getattr(self, "disc_count", None):
                disc += f"/{disc_count}"
            self._tags.add(id3.TPOS(text=disc))

        if track_number := getattr(self, "track_number", None):
            track = str(track_number)
            if track_count := getattr(self, "track_count", None):
                track += f"/{track_count}"
            self._tags.add(id3.TRCK(text=track))

        if self.artwork:
            IMAGE_FORMATS = dict.fromkeys(
                ["jpg", "jpeg", "jpe", "jif", "jfif", "jfi"], "image/jpeg"
            ) | {"png": "image/png"}

            if isinstance(self.artwork, str):
                with (
                    urllib.request.urlopen(self.artwork)
                    if "http" in self.artwork
                    else open(self.artwork, "rb")
                ) as f:
                    self.artwork = f.read()
            self._tags.add(
                id3.APIC(data=self.artwork, mime=IMAGE_FORMATS[self._artwork_format])
            )

        self._tags.save()


class _VorbisComment:
    """
    Vorbis comment handler for FLAC and Ogg audio files.

    .. attention::

       This class should *not* be instantiated manually. Instead, use
       :class:`FLACAudio` or :class:`OggAudio` to process metadata for
       FLAC and Ogg audio files, respectively.

    Parameters
    ----------
    filename : `str`
        Audio filename.

    tags : `mutagen.id3.ID3`
        ID3 metadata.
    """

    _FIELDS = {
        # field: (Vorbis comment key, typecasting function)
        "album": ("album", None),
        "album_artist": ("albumartist", None),
        "artist": ("artist", None),
        "comment": ("description", None),
        "composer": ("composer", None),
        "copyright": ("copyright", None),
        "date": ("date", None),
        "genre": ("genre", None),
        "isrc": ("isrc", None),
        "lyrics": ("lyrics", None),
        "tempo": ("bpm", str),
        "title": ("title", None),
    }
    _FIELDS_SPECIAL = {
        "compilation": ("compilation", lambda x: str(int(x))),
        "disc_number": ("discnumber", str),
        "disc_count": ("disctotal", str),
        "track_number": ("tracknumber", str),
        "track_count": ("tracktotal", str),
    }

    def __init__(self, filename: str, tags: id3.ID3) -> None:
        """
        Create a Vorbis comment handler.
        """

        self._filename = filename
        self._tags = tags
        self._from_file()

    def _from_file(self) -> None:
        """
        Get metadata from the tags embedded in the FLAC audio file.
        """

        for field, (key, _) in self._FIELDS.items():
            value = self._tags.get(key)
            if value:
                if list not in self._FIELDS_TYPES[field]:
                    value = utility.format_multivalue(value, False, primary=True)
                    if type(value) not in self._FIELDS_TYPES[field]:
                        try:
                            value = self._FIELDS_TYPES[field][0](value)
                        except ValueError:
                            continue
                else:
                    if type(value[0]) not in self._FIELDS_TYPES[field]:
                        try:
                            value = [self._FIELDS_TYPES[field][0](v) for v in value]
                        except ValueError:
                            continue
                    if len(value) == 1:
                        value = value[0]
            else:
                value = None
            setattr(self, field, value)

        self.compilation = (
            bool(int(self._tags.get("compilation")[0]))
            if "compilation" in self._tags
            else None
        )

        if "discnumber" in self._tags:
            disc_number = self._tags.get("discnumber")[0]
            if "/" in disc_number:
                self.disc_number, self.disc_count = (
                    int(d) for d in disc_number.split("/")
                )
            else:
                self.disc_number = int(disc_number)
                self.disc_count = self._tags.get("disctotal")
                if self.disc_count:
                    self.disc_count = int(self.disc_count[0])
        else:
            self.disc_number = self.disc_count = None

        if "tracknumber" in self._tags:
            track_number = self._tags.get("tracknumber")[0]
            if "/" in track_number:
                self.track_number, self.track_count = (
                    int(t) for t in track_number.split("/")
                )
            else:
                self.track_number = int(track_number)
                self.track_count = self._tags.get("tracktotal")
                if self.track_count:
                    self.track_count = int(self.track_count[0])
        else:
            self.track_number = self.track_count = None

        if hasattr(self._handle, "pictures") and self._handle.pictures:
            self.artwork = self._handle.pictures[0].data
            self._artwork_format = self._handle.pictures[0].mime.split("/")[1]
        elif "metadata_block_picture" in self._tags:
            IMAGE_FILE_SIGS = {
                "jpg": b"\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01",
                "png": b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a",
            }
            self.artwork = base64.b64decode(
                self._tags["metadata_block_picture"][0].encode()
            )
            for img_fmt, file_sig in IMAGE_FILE_SIGS.items():
                if file_sig in self.artwork:
                    self.artwork = self.artwork[
                        re.search(file_sig, self.artwork).span()[0] :
                    ]
                    self._artwork_format = img_fmt
        else:
            self.artwork = self._artwork_format = None

    def write_metadata(self) -> None:
        """
        Write metadata to file.
        """

        for field, (key, func) in (self._FIELDS | self._FIELDS_SPECIAL).items():
            value = getattr(self, field)
            if value:
                value = utility.format_multivalue(
                    value, self._multivalue, sep=self._sep
                )
                self._tags[key] = func(value) if func else value

        if self.artwork:
            artwork = flac.Picture()
            artwork.type = id3.PictureType.COVER_FRONT
            artwork.mime = f"image/{self._artwork_format}"
            if isinstance(self.artwork, str):
                with (
                    urllib.request.urlopen(self.artwork)
                    if "http" in self.artwork
                    else open(self.artwork, "rb")
                ) as f:
                    self.artwork = f.read()
            artwork.data = self.artwork
            try:
                self._handle.clear_pictures()
                self._handle.add_picture(artwork)
            except ValueError:
                self._tags["metadata_block_picture"] = base64.b64encode(
                    artwork.write()
                ).decode()

        self._handle.save()


class Audio:
    r"""
    Generic audio file handler.

    Subclasses for specific audio containers or formats include

    * :class:`FLACAudio` for audio encoded using the Free
      Lossless Audio Codec (FLAC),
    * :class:`MP3Audio` for audio encoded and stored in the MPEG Audio
      Layer III (MP3) format,
    * :class:`MP4Audio` for audio encoded in the Advanced
      Audio Coding (AAC) format, encoded using the Apple Lossless
      Audio Codec (ALAC), or stored in a MPEG-4 Part 14 (MP4, M4A)
      container,
    * :class:`OggAudio` for Opus or Vorbis audio stored in an Ogg file,
      and
    * :class:`WAVEAudio` for audio encoded using linear pulse-code
      modulation (LPCM) and in the Waveform Audio File Format (WAVE).

    .. note::

       This class can instantiate a specific file handler from the list
       above for an audio file by examining its file extension. However,
       there may be instances when this detection fails, especially when
       the audio codec and format combination is rarely seen. As such,
       it is always best to directly use one of the subclasses above to
       create a file handler for your audio file when its audio codec
       and format are known.

    Parameters
    ----------
    file : `str` or `pathlib.Path`
        Audio filename or path.

    pattern : `tuple`, keyword-only, optional
        Regular expression search pattern and the corresponding metadata
        field(s).

        .. container::

           **Valid values**:

           The supported metadata fields are

           * :code:`"artist"` for the track artist,
           * :code:`"title"` for the track title, and
           * :code:`"track_number"` for the track number.

           **Examples**:

           * :code:`("(.*) - (.*)", ("artist", "title"))` matches
             filenames like "Taylor Swift - Cruel Summer.flac".
           * :code:`("(\\d*) - (.*)", ("track_number", "title"))` matches
             filenames like "04 - The Man.m4a".
           * :code:`("(\\d*) (.*)", ("track_number", "title"))` matches
             filenames like "13 You Need to Calm Down.mp3".

    multivalue : `bool`
        Determines whether multivalue tags are supported. If
        :code:`False`, the items in `value` are concatenated using the
        separator(s) specified in `sep`.

    sep : `str` or `tuple`, keyword-only, default: :code:`(", ", " & ")`
        Separator(s) to use to concatenate multivalue tags. If a
        :code:`str` is provided, it is used to concatenate all values.
        If a :code:`tuple` is provided, the first :code:`str` is used to
        concatenate the first :math:`n - 1` values, and the second
        :code:`str` is used to append the final value.

    Attributes
    ----------
    album : `str`
        Album title.

    album_artist : `str` or `list`
        Album artist(s).

    artist : `str` or `list`
        Artist(s).

    artwork : `bytes` or `str`
        Byte-representation of, URL leading to, or filename of file
        containing the cover artwork.

    bit_depth : `int`
        Bits per sample.

    bitrate : `int`
        Bitrate in bytes per second (B/s).

    channel_count : `int`
        Number of audio channels.

    codec : `str`
        Audio codec.

    comment : `str`
        Comment(s).

    compilation : `bool`
        Whether the album is a compilation of songs by various artists.

    composer : `str` or `list`
        Composers, lyrics, and/or writers.

    copyright : `str`
        Copyright information.

    date : `str`
        Release date.

    disc_number : `int`
        Disc number.

    disc_count : `int`
        Total number of discs.

    genre : `str` or `list`
        Genre.

    isrc : `str`
        International Standard Recording Code (ISRC).

    lyrics : `str`
        Lyrics.

    sample_rate : `int`
        Sample rate in Hz.

    tempo : `int`
        Tempo in beats per minute (bpm).

    title : `str`
        Track title.

    track_number : `int`
        Track number.

    track_count : `int`
        Total number of tracks.
    """

    _FIELDS_TYPES = {
        "_artwork_format": (str,),
        "album": (str,),
        "album_artist": (str, list),
        "artist": (str, list),
        "artwork": (bytes, str),
        "comment": (str,),
        "compilation": (bool,),
        "composer": (str, list),
        "copyright": (str,),
        "date": (str,),
        "disc_number": (int,),
        "disc_count": (int,),
        "genre": (str, list),
        "isrc": (str,),
        "lyrics": (str,),
        "tempo": (int,),
        "title": (str,),
        "track_number": (int,),
        "track_count": (int,),
    }

    def __init__(
        self,
        file: Union[str, pathlib.Path],
        *,
        pattern: tuple[str, tuple[str]] = None,
        multivalue: bool = False,
        sep: Union[str, list[str]] = (", ", " & "),
    ) -> None:
        """
        Instantiate an audio file handler.
        """

        self._file = pathlib.Path(file).resolve()
        self._pattern = pattern
        self._multivalue = multivalue
        self._sep = sep

    def __new__(cls, *args, **kwargs) -> None:
        """
        Create an audio file handler.

        Parameters
        ----------
        file : `str` or `pathlib.Path`
            Audio file.
        """

        if cls == Audio:
            file = kwargs.get("file")
            if file is None:
                file = args[0]
            file = pathlib.Path(file)
            if not file.is_file():
                raise FileNotFoundError(f"'{file}' not found.")

            ext = file.suffix[1:].lower()
            for a in Audio.__subclasses__():
                if ext in a._EXTENSIONS:
                    return a(*args, **kwargs)
            raise TypeError(f"'{file}' has an unsupported audio format.")

        return super(Audio, cls).__new__(cls)

    def _from_filename(self) -> None:
        """
        Get track information from the filename.
        """

        if self._pattern:
            groups = re.findall(self._pattern[0], self._file.stem)
            if groups:
                missing = tuple(
                    k in {"artist", "title", "track_number"}
                    and getattr(self, k) is None
                    for k in self._pattern[1]
                )
                for flag, attr, val in zip(missing, self._pattern[1], groups[0]):
                    if flag:
                        setattr(self, attr, self._FIELDS_TYPES[attr][0](val))

    def convert(
        self,
        codec: str,
        container: str = None,
        options: str = None,
        *,
        filename: str = None,
        preserve: bool = True,
    ) -> None:
        """
        Convert the current audio file to another format.

        .. admonition:: Software dependency

           Requires `FFmpeg <https://ffmpeg.org/>`_.

        .. note::

           The audio file handler is automatically updated to reflect
           the new audio file format. For example, converting a FLAC
           audio file to an ALAC audio file will change the file handler
           from a :class:`FLACAudio` object to an :class:`MP4Audio`
           object.

        Parameters
        ----------
        codec : `str`
            New audio codec or coding format.

            .. container::

               **Valid values**:

               * :code:`"aac"`, :code:`"m4a"`, :code:`"mp4"`, or
                 :code:`"mp4a"` for lossy AAC audio.
               * :code:`"alac"` for lossless ALAC audio.
               * :code:`"flac"` for lossless FLAC audio.
               * :code:`"mp3"` for lossy MP3 audio.
               * :code:`"ogg"` or :code:`"opus"` for lossy Opus audio
               * :code:`"vorbis"` for lossy Vorbis audio.
               * :code:`"lpcm"`, :code:`"wav"`, or :code:`"wave"` for
                 lossless LPCM audio.

        container : `str`, optional
            New audio file container. If not specified, the best
            container is determined based on `codec`.

            .. container::

               **Valid values**:

               * :code:`"flac"` for a FLAC audio container, which only
                 supports FLAC audio.
               * :code:`"m4a"`, :code:`"mp4"`, or :code:`"mp4a"` for
                 a MP4 audio container, which supports AAC and ALAC
                 audio.
               * :code:`"mp3"` for a MP3 audio container, which only
                 supports MP3 audio.
               * :code:`"ogg"` for an Ogg audio container, which
                 supports FLAC, Opus, and Vorbis audio.
               * :code:`"wav"` or :code:`"wave"` for an WAVE audio
                 container, which only supports LPCM audio.

        options : `str`, optional
            FFmpeg command-line options, excluding the input and output
            files, the :code:`-y` flag (to overwrite files), and the
            :code:`-c:v copy` argument (to preserve cover art for
            containers that support it).

            .. container::

               **Defaults**:

               * AAC audio: :code:`"-c:a aac -b:a 256k"` (or
                 :code:`"-c:a libfdk_aac -b:a 256k"` if FFmpeg was
                 compiled with :code:`--enable-libfdk-aac`)
               * ALAC audio: :code:`"-c:a alac"`
               * FLAC audio: :code:`"-c:a flac"`
               * MP3 audio: :code:`"-c:a libmp3lame -q:a 0"`
               * Opus audio: :code:`"-c:a libopus -b:a 256k -vn"`
               * Vorbis audio:
                 :code:`"-c:a vorbis -strict experimental -vn"` (or
                 :code:`"-c:a libvorbis -vn"` if FFmpeg was compiled
                 with :code:`--enable-libvorbis`)
               * WAVE audio: :code:`"-c:a pcm_s16le"` or
                 :code:`"-c:a pcm_s24le"`, depending on the bit depth of
                 the original audio file.

        filename : `str`, keyword-only, optional
            Filename of the converted audio file. If not provided, the
            filename of the original audio file, but with the
            appropriate new extension appended, is used.

        preserve : `bool`, keyword-only, default: :code:`True`
            Determines whether the original audio file is kept.
        """

        if not FOUND_FFMPEG:
            emsg = "Audio conversion is unavailable because FFmpeg " "was not found."
            raise RuntimeError(emsg)

        _codec = codec.capitalize() if codec in {"opus", "vorbis"} else codec.upper()
        codec = codec.lower()
        if codec in {"m4a", "mp4", "mp4a"}:
            codec = "aac"
        elif codec == "ogg":
            codec = "opus"
        elif codec in "wave":
            codec = "lpcm"

        if container:
            container = container.lower()
            if container == "m4a":
                container = "mp4"
            elif container == "wave":
                container = "wav"

            try:
                acls = next(
                    a
                    for a in Audio.__subclasses__()
                    if codec in a._CODECS and container in a._EXTENSIONS
                )
            except StopIteration:
                emsg = (
                    f"{_codec} audio is incompatible with "
                    f"the {container.upper()} container."
                )
                raise RuntimeError(emsg)
        else:
            try:
                acls = next(a for a in Audio.__subclasses__() if codec in a._CODECS)
                container = acls._EXTENSIONS[0]
            except StopIteration:
                raise RuntimeError(f"The '{_codec}' codec is not supported.")

        if ("mp4" if codec == "aac" else codec) in self.codec and isinstance(
            self, acls
        ):
            wmsg = (
                f"'{self._file}' already has {_codec} "
                f"audio in a {container.upper()} container. "
                "Re-encoding may lead to quality degradation from "
                "generation loss."
            )
            logging.warning(wmsg)

        ext = f".{acls._EXTENSIONS[0]}"
        if filename is None:
            filename = self._file.with_suffix(ext)
        else:
            if isinstance(filename, str):
                if "/" not in filename:
                    filename = f"{self._file.parent}/{filename}"
            filename = pathlib.Path(filename).resolve()
            if filename.suffix != ext:
                filename = filename.with_suffix(ext)
            filename.parent.mkdir(parents=True, exist_ok=True)
        if self._file == filename:
            filename = filename.with_stem(f"{filename.stem}_")

        if options is None:
            if codec == "lpcm":
                options = acls._CODECS[codec]["ffmpeg"].format(
                    self.bit_depth if hasattr(self, "bit_depth") else 16
                )
            else:
                options = acls._CODECS[codec]["ffmpeg"]

        subprocess.run(
            f'ffmpeg -y -i "{self._file}" {options} -loglevel error '
            f'-stats "{filename}"',
            shell=True,
        )
        if not preserve:
            self._file.unlink()

        obj = acls(filename)
        self.__class__ = obj.__class__
        self.__dict__ = obj.__dict__ | {
            key: value
            for (key, value) in self.__dict__.items()
            if key in self._FIELDS_TYPES
        }

    def set_metadata_using_itunes(
        self,
        data: dict[str, Any],
        *,
        album_data: dict[str, Any] = None,
        artwork_size: Union[int, str] = 1400,
        artwork_format: str = "jpg",
        overwrite: bool = False,
    ) -> None:
        """
        Populate tags using data retrieved from the iTunes Search API.

        Parameters
        ----------
        data : `dict`
            Information about the track in JSON format obtained using
            the iTunes Search API via
            :meth:`minim.itunes.SearchAPI.search` or
            :meth:`minim.itunes.SearchAPI.lookup`.

        album_data : `dict`, keyword-only, optional
            Information about the track's album in JSON format obtained
            using the iTunes Search API via
            :meth:`minim.itunes.SearchAPI.search` or
            :meth:`minim.itunes.SearchAPI.lookup`. If not provided,
            album artist and copyright information is unavailable.

        artwork_size : `int` or `str`, keyword-only, default: :code:`1400`
            Resized artwork size in pixels. If
            :code:`artwork_size="raw"`, the uncompressed high-resolution
            image is retrieved, regardless of size.

        artwork_format : `str`, keyword-only, :code:`{"jpg", "png"}`
            Artwork file format. If :code:`artwork_size="raw"`, the file
            format of the uncompressed high-resolution image takes
            precedence.

        overwrite : `bool`, keyword-only, default: :code:`False`
            Determines whether existing metadata should be overwritten.
        """

        if self.album is None or overwrite:
            self.album = data["collectionName"]
        if self.artist is None or overwrite:
            self.artist = data["artistName"]
        if self.artwork is None or overwrite:
            self.artwork = data["artworkUrl100"]
            if self.artwork:
                if artwork_size == "raw":
                    if "Feature" in self.artwork:
                        self.artwork = (
                            "https://a5.mzstatic.com/us/r1000/0"
                            f"/{re.search(r'Feature.*?(jpg|png|tif)(?=/|$)', self.artwork)[0]}"
                        )
                    elif "Music" in self.artwork:
                        self.artwork = (
                            "https://a5.mzstatic.com/"
                            f"{re.search(r'Music.*?(jpg|png|tif)(?=/|$)', self.artwork)[0]}"
                        )
                    self._artwork_format = pathlib.Path(self.artwork).suffix[1:]
                else:
                    self.artwork = self.artwork.replace(
                        "100x100bb.jpg",
                        f"{artwork_size}x{artwork_size}bb.{artwork_format}",
                    )
                    self._artwork_format = artwork_format
                with urllib.request.urlopen(self.artwork) as r:
                    self.artwork = r.read()
                if self._artwork_format == "tif":
                    if FOUND_PILLOW:
                        with Image.open(BytesIO(self.artwork)) as a:
                            with BytesIO() as b:
                                a.save(b, format="png")
                                self.artwork = b.getvalue()
                        self._artwork_format = "png"
                    else:
                        wmsg = (
                            "The Pillow library is required to process "
                            "TIFF images, but was not found. No artwork "
                            "will be embedded for the current track."
                        )
                        warnings.warn(wmsg)
                        self.artwork = self._artwork_format = None
        if self.compilation is None or overwrite:
            self.compilation = self.album_artist == "Various Artists"
        if "releaseDate" in data and (self.date is None or overwrite):
            self.date = data["releaseDate"]
        if self.disc_number is None or overwrite:
            self.disc_number = data["discNumber"]
        if self.disc_count is None or overwrite:
            self.disc_count = data["discCount"]
        if self.genre is None or overwrite:
            self.genre = data["primaryGenreName"]
        if self.title is None or overwrite:
            self.title = max(data["trackName"], data["trackCensoredName"])
        if self.track_number is None or overwrite:
            self.track_number = data["trackNumber"]
        if self.track_count is None or overwrite:
            self.track_count = data["trackCount"]

        if album_data:
            if self.album_artist is None or overwrite:
                self.album_artist = album_data["artistName"]
            if self.copyright or overwrite:
                self.copyright = album_data["copyright"]

    def set_metadata_using_qobuz(
        self,
        data: dict[str, Any],
        *,
        artwork_size: str = "large",
        comment: str = None,
        overwrite: bool = False,
    ) -> None:
        """
        Populate tags using data retrieved from the Qobuz API.

        Parameters
        ----------
        data : `dict`
            Information about the track in JSON format obtained using
            the Qobuz API via :meth:`minim.qobuz.PrivateAPI.get_track`
            or :meth:`minim.qobuz.PrivateAPI.search`.

        artwork_size : `str`, keyword-only, default: :code:`"large"`
            Artwork size.

            **Valid values**: :code:`"large"`, :code:`"small"`, or
            :code:`"thumbnail"`.

        comment : `str`, keyword-only, optional
            Comment or description.

        overwrite : `bool`, keyword-only, default: :code:`False`
            Determines whether existing metadata should be overwritten.
        """

        if self.album is None or overwrite:
            self.album = data["album"]["title"]
            if album_artists := data["album"].get("artists"):
                album_feat_artist = [
                    a["name"] for a in album_artists if "featured-artist" in a["roles"]
                ]
                if album_feat_artist and "feat." not in self.album:
                    self.album += (
                        " [feat. {}]" if "(" in self.album else " (feat. {})"
                    ).format(utility.format_multivalue(album_feat_artist, False))
            if data["album"]["version"]:
                self.album += (" [{}]" if "(" in self.album else " ({})").format(
                    data["album"]["version"]
                )
            self.album = self.album.replace("  ", " ")
        if self.album_artist is None or overwrite:
            if album_artists := data["album"].get("artists"):
                album_artist = [
                    a["name"] for a in album_artists if "main-artist" in a["roles"]
                ]
                album_main_artist = data["album"]["artist"]["name"]
                if album_main_artist in album_artist:
                    if (
                        i := (
                            album_artist.index(album_main_artist)
                            if album_main_artist in album_artist
                            else 0
                        )
                    ) != 0:
                        album_artist.insert(0, album_artist.pop(i))
                    self.album_artist = album_artist
                else:
                    self.album_artist = album_main_artist
            else:
                self.album_artist = data["album"]["artist"]["name"]

        credits = _parse_performers(
            data["performers"], roles=["MainArtist", "FeaturedArtist", "Composers"]
        )
        if self.artist is None or overwrite:
            self.artist = credits.get("main_artist") or data["performer"]["name"]
        if self.artwork is None or overwrite:
            if artwork_size not in (ARTWORK_SIZES := {"large", "small", "thumbnail"}):
                emsg = (
                    f"Invalid artwork size '{artwork_size}'. "
                    f"Valid values: {ARTWORK_SIZES}."
                )
                raise ValueError(emsg)
            self.artwork = data["album"]["image"][artwork_size]
            self._artwork_format = pathlib.Path(self.artwork).suffix[1:]
        if self.comment is None or overwrite:
            self.comment = comment
        if self.composer is None or overwrite:
            self.composer = credits.get("composers") or (
                data["composer"]["name"] if hasattr(data, "composer") else None
            )
        if self.copyright is None or overwrite:
            self.copyright = data["album"].get("copyright")
        if self.date is None or overwrite:
            self.date = min(
                (
                    datetime.datetime.utcfromtimestamp(dt)
                    if isinstance(dt, int)
                    else (
                        datetime.datetime.strptime(dt, "%Y-%m-%d")
                        if isinstance(dt, str)
                        else datetime.datetime.max
                    )
                )
                for dt in (
                    data.get(k)
                    for k in {
                        "release_date_original",
                        "release_date_download",
                        "release_date_stream",
                        "release_date_purchase",
                        "purchasable_at",
                        "streamable_at",
                    }
                )
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
        if self.disc_number is None or overwrite:
            self.disc_number = data["media_number"]
        if self.disc_count is None or overwrite:
            self.disc_count = data["album"]["media_count"]
        if self.genre is None or overwrite:
            self.genre = data["album"]["genre"]["name"]
        if self.isrc is None or overwrite:
            self.isrc = data["isrc"]
        if self.title is None or overwrite:
            self.title = data["title"]
            if (
                feat_artist := credits.get("featured_artist")
            ) and "feat." not in self.title:
                self.title += (
                    " [feat. {}]" if "(" in self.title else " (feat. {})"
                ).format(utility.format_multivalue(feat_artist, False))
            if data["version"]:
                self.title += (" [{}]" if "(" in self.title else " ({})").format(
                    data["version"]
                )
            self.title = self.title.replace("  ", " ")
        if self.track_number is None or overwrite:
            self.track_number = data["track_number"]
        if self.track_count is None or overwrite:
            self.track_count = data["album"]["tracks_count"]

        if data["album"].get("release_type") == "single" and self.album == self.title:
            self.album += " - Single"
            self.album_artist = self.artist = max(
                self.artist, self.album_artist, key=len
            )

    def set_metadata_using_spotify(
        self,
        data: dict[str, Any],
        *,
        audio_features: dict[str, Any] = None,
        lyrics: Union[str, dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> None:
        """
        Populate tags using data retrieved from the Spotify Web API
        and Spotify Lyrics service.

        Parameters
        ----------
        data : `dict`
            Information about the track in JSON format obtained using
            the Spotify Web API via
            :meth:`minim.spotify.WebAPI.get_track`.

        audio_features : `dict`, keyword-only, optional
            Information about the track's audio features obtained using
            the Spotify Web API via
            :meth:`minim.spotify.WebAPI.get_track_audio_features`.
            If not provided, tempo information is unavailable.

        lyrics : `str` or `dict`, keyword-only
            Information about the track's formatted or time-synced
            lyrics obtained using the Spotify Lyrics service via
            :meth:`minim.spotify.PrivateLyricsService.get_lyrics`. If not
            provided, lyrics are unavailable.

        overwrite : `bool`, keyword-only, default: :code:`False`
            Determines whether existing metadata should be overwritten.
        """

        if self.album is None or overwrite:
            self.album = data["album"]["name"]
            if data["album"]["album_type"] == "single":
                self.album += " - Single"
        if self.album_artist is None or overwrite:
            self.album_artist = [a["name"] for a in data["album"]["artists"]]
        if self.artist is None or overwrite:
            self.artist = [a["name"] for a in data["artists"]]
        if self.artwork is None or overwrite:
            with urllib.request.urlopen(data["album"]["images"][0]["url"]) as r:
                self.artwork = r.read()
            self._artwork_format = "jpg"
        if self.compilation is None or overwrite:
            self.compilation = data["album"]["album_type"] == "compilation"
        if self.date is None or overwrite:
            self.date = data["album"]["release_date"]
        if self.disc_number is None or overwrite:
            self.disc_number = data["disc_number"]
        if self.isrc is None or overwrite:
            self.isrc = data["external_ids"]["isrc"]
        if (self.lyrics is None or overwrite) and lyrics:
            self.lyrics = (
                lyrics
                if isinstance(lyrics, str)
                else "\n".join(line["words"] for line in lyrics["lyrics"]["lines"])
            )
        if (self.tempo is None or overwrite) and audio_features:
            self.tempo = round(audio_features["tempo"])
        if self.title is None or overwrite:
            self.title = data["name"]
        if self.track_number is None or overwrite:
            self.track_number = data["track_number"]
        if self.track_count is None or overwrite:
            self.track_count = data["album"]["total_tracks"]

    def set_metadata_using_tidal(
        self,
        data: dict[str, Any],
        *,
        album_data: dict[str, Any] = None,
        artwork_size: int = 1280,
        composers: Union[str, list[str], dict[str, Any]] = None,
        lyrics: dict[str, Any] = None,
        comment: str = None,
        overwrite: bool = False,
    ) -> None:
        """
        Populate tags using data retrieved from the TIDAL API.

        Parameters
        ----------
        data : `dict`
            Information about the track in JSON format obtained using
            the TIDAL API via :meth:`minim.tidal.API.get_track`,
            :meth:`minim.tidal.API.search`,
            :meth:`minim.tidal.PrivateAPI.get_track`, or
            :meth:`minim.tidal.PrivateAPI.search`.

        album_data : `dict`, keyword-only, optional
            Information about the track's album in JSON format obtained
            using the TIDAL API via :meth:`minim.tidal.API.get_album`,
            :meth:`minim.tidal.API.search`,
            :meth:`minim.tidal.PrivateAPI.get_album`, or
            :meth:`minim.tidal.PrivateAPI.search`. If not provided,
            album artist and disc and track numbering information is
            unavailable.

        artwork_size : `int`, keyword-only, default: :code:`1280`
            Maximum artwork size in pixels.

            **Valid values**: `artwork_size` should be between
            :code:`80` and :code:`1280`.

        composers : `str`, `list`, or `dict`, keyword-only, optional
            Information about the track's composers in a formatted
            `str`, a `list`, or a `dict` obtained using the TIDAL API
            via :meth:`minim.tidal.PrivateAPI.get_track_composers`,
            :meth:`minim.tidal.PrivateAPI.get_track_contributors`, or
            :meth:`minim.tidal.PrivateAPI.get_track_credits`. If not
            provided, songwriting credits are unavailable.

        lyrics : `str` or `dict`, keyword-only, optional
            The track's lyrics obtained using the TIDAL API via
            :meth:`minim.tidal.PrivateAPI.get_track_lyrics`.

        comment : `str`, keyword-only, optional
            Comment or description.

        overwrite : `bool`, keyword-only, default: :code:`False`
            Determines whether existing metadata should be overwritten.
        """

        if "resource" in data:
            data = data["resource"]
        if self.album is None or overwrite:
            self.album = data["album"]["title"]
        if (self.comment is None or overwrite) and comment:
            self.comment = comment
        if (self.composer is None or overwrite) and composers:
            COMPOSER_TYPES = {"Composer", "Lyricist", "Writer"}
            if isinstance(composers, dict):
                self.composer = sorted(
                    {
                        c["name"]
                        for c in composers["items"]
                        if c["role"] in COMPOSER_TYPES
                    }
                )
            elif isinstance(composers[0], dict):
                self.composer = sorted(
                    {
                        c["name"]
                        for r in composers
                        for c in r["contributors"]
                        if r["type"] in COMPOSER_TYPES
                    }
                )
            else:
                self.composer = composers
        if self.copyright is None or overwrite:
            self.copyright = data["copyright"]
        if self.disc_number is None or overwrite:
            self.disc_number = data["volumeNumber"]
        if self.isrc is None or overwrite:
            self.isrc = data["isrc"]
        if (self.lyrics is None or overwrite) and lyrics:
            self.lyrics = lyrics if isinstance(lyrics, str) else lyrics["lyrics"]
        if self.title is None or overwrite:
            self.title = data["title"]
        if self.track_number is None or overwrite:
            self.track_number = data["trackNumber"]

        if "artifactType" in data:
            if self.artist is None or overwrite:
                self.artist = [a["name"] for a in data["artists"] if a["main"]]
            if self.artwork is None or overwrite:
                image_urls = sorted(
                    data["album"]["imageCover"], key=lambda x: x["width"], reverse=True
                )
                self.artwork = (
                    image_urls[-1]["url"]
                    if artwork_size < image_urls[-1]["width"]
                    else next(
                        u["url"] for u in image_urls if u["width"] <= artwork_size
                    )
                )
                self._artwork_format = pathlib.Path(self.artwork).suffix[1:]
        else:
            if self.artist is None or overwrite:
                self.artist = [
                    a["name"] for a in data["artists"] if a["type"] == "MAIN"
                ]
            if self.artwork is None or overwrite:
                artwork_size = (
                    80
                    if artwork_size < 80
                    else next(
                        s
                        for s in [1280, 1080, 750, 640, 320, 160, 80]
                        if s <= artwork_size
                    )
                )
                self.artwork = (
                    "https://resources.tidal.com/images"
                    f"/{data['album']['cover'].replace('-', '/')}"
                    f"/{artwork_size}x{artwork_size}.jpg"
                )
                self._artwork_format = "jpg"
            if self.date is None or overwrite:
                self.date = f"{data['streamStartDate'].split('.')[0]}Z"

        if album_data:
            if self.copyright is None or overwrite:
                self.copyright = album_data["copyright"]
            if self.disc_count is None or overwrite:
                self.disc_count = album_data["numberOfVolumes"]
            if self.track_count is None or overwrite:
                self.track_count = album_data["numberOfTracks"]

            if "barcodeId" in album_data:
                if self.album_artist is None or overwrite:
                    self.album_artist = [
                        a["name"] for a in album_data["artists"] if a["main"]
                    ]
                if self.date is None or overwrite:
                    self.date = f"{album_data['releaseDate']}T00:00:00Z"
            else:
                if self.album_artist is None or overwrite:
                    self.album_artist = [
                        a["name"] for a in album_data["artists"] if a["type"] == "MAIN"
                    ]


class FLACAudio(Audio, _VorbisComment):
    r"""
    FLAC audio file handler.

    .. seealso::

       For a full list of attributes and their descriptions, see
       :class:`Audio`.

    Parameters
    ----------
    file : `str` or `pathlib.Path`
        FLAC audio filename or path.

    pattern : `tuple`, keyword-only, optional
        Regular expression search pattern and the corresponding metadata
        field(s).

        .. container::

           **Valid values**:

           The supported metadata fields are

           * :code:`"artist"` for the track artist,
           * :code:`"title"` for the track title, and
           * :code:`"track_number"` for the track number.

           **Examples**:

           * :code:`("(.*) - (.*)", ("artist", "title"))` matches
             filenames like "Taylor Swift - Fearless.flac".
           * :code:`("(\\d*) - (.*)", ("track_number", "title"))` matches
             filenames like "03 - Love Story.flac".
           * :code:`("(\\d*) (.*)", ("track_number", "title"))` matches
             filenames like "06 You Belong with Me.flac".

    multivalue : `bool`
        Determines whether multivalue tags are supported. If
        :code:`False`, the items in `value` are concatenated using the
        separator(s) specified in `sep`.

    sep : `str` or `tuple`, keyword-only, default: :code:`(", ", " & ")`
        Separator(s) to use to concatenate multivalue tags. If a
        :code:`str` is provided, it is used to concatenate all values.
        If a :code:`tuple` is provided, the first :code:`str` is used to
        concatenate the first :math:`n - 1` values, and the second
        :code:`str` is used to append the final value.
    """

    _CODECS = {"flac": {"ffmpeg": "-c:a flac -c:v copy"}}
    _EXTENSIONS = ["flac"]

    def __init__(
        self,
        file: Union[str, pathlib.Path],
        *,
        pattern: tuple[str, tuple[str]] = None,
        multivalue: bool = False,
        sep: Union[str, list[str]] = (", ", " & "),
    ) -> None:
        """
        Create a FLAC audio file handler.
        """

        Audio.__init__(self, file, pattern=pattern, multivalue=multivalue, sep=sep)
        self._handle = flac.FLAC(file)
        if self._handle.tags is None:
            self._handle.add_tags()
        _VorbisComment.__init__(self, self._file.name, self._handle.tags)
        self._from_filename()

        self.bit_depth = self._handle.info.bits_per_sample
        self.bitrate = self._handle.info.bitrate
        self.channel_count = self._handle.info.channels
        self.codec = "flac"
        self.sample_rate = self._handle.info.sample_rate


class MP3Audio(Audio, _ID3):
    r"""
    MP3 audio file handler.

    .. seealso::

       For a full list of attributes and their descriptions, see
       :class:`Audio`.

    Parameters
    ----------
    file : `str` or `pathlib.Path`
        MP3 audio filename or path.

    pattern : `tuple`, keyword-only, optional
        Regular expression search pattern and the corresponding metadata
        field(s).

        .. container::

           **Valid values**:

           The supported metadata fields are

           * :code:`"artist"` for the track artist,
           * :code:`"title"` for the track title, and
           * :code:`"track_number"` for the track number.

           **Examples**:

           * :code:`("(.*) - (.*)", ("artist", "title"))` matches
             filenames like "Taylor Swift - Red.mp3".
           * :code:`("(\\d*) - (.*)", ("track_number", "title"))` matches
             filenames like "04 - I Knew You Were Trouble.mp3".
           * :code:`("(\\d*) (.*)", ("track_number", "title"))` matches
             filenames like "06 22.mp3".

    multivalue : `bool`
        Determines whether multivalue tags are supported. If
        :code:`False`, the items in `value` are concatenated using the
        separator(s) specified in `sep`.

    sep : `str` or `tuple`, keyword-only, default: :code:`(", ", " & ")`
        Separator(s) to use to concatenate multivalue tags. If a
        :code:`str` is provided, it is used to concatenate all values.
        If a :code:`tuple` is provided, the first :code:`str` is used to
        concatenate the first :math:`n - 1` values, and the second
        :code:`str` is used to append the final value.
    """

    _CODECS = {"mp3": {"ffmpeg": "-c:a libmp3lame -q:a 0 -c:v copy"}}
    _EXTENSIONS = ["mp3"]

    def __init__(
        self,
        file: Union[str, pathlib.Path],
        *,
        pattern: tuple[str, tuple[str]] = None,
        multivalue: bool = False,
        sep: Union[str, list[str]] = (", ", " & "),
    ) -> None:
        """
        Create a MP3 audio file handler.
        """

        _handle = mp3.MP3(file)
        _handle.tags.filename = str(file)
        Audio.__init__(self, file, pattern=pattern, multivalue=multivalue, sep=sep)
        _ID3.__init__(self, self._file.name, _handle.tags)
        self._from_filename()

        self.bit_depth = None
        self.bitrate = _handle.info.bitrate
        self.channel_count = _handle.info.channels
        self.codec = "mp3"
        self.sample_rate = _handle.info.sample_rate


class MP4Audio(Audio):
    r"""
    MP4 audio file handler.

    .. seealso::

       For a full list of attributes and their descriptions, see
       :class:`Audio`.

    Parameters
    ----------
    file : `str` or `pathlib.Path`
        MP4 audio filename or path.

    pattern : `tuple`, keyword-only, optional
        Regular expression search pattern and the corresponding metadata
        field(s).

        .. container::

           **Valid values**:

           The supported metadata fields are

           * :code:`"artist"` for the track artist,
           * :code:`"title"` for the track title, and
           * :code:`"track_number"` for the track number.

           **Examples**:

           * :code:`("(.*) - (.*)", ("artist", "title"))` matches
             filenames like "Taylor Swift - Mine.m4a".
           * :code:`("(\\d*) - (.*)", ("track_number", "title"))` matches
             filenames like "04 - Speak Now.m4a".
           * :code:`("(\\d*) (.*)", ("track_number", "title"))` matches
             filenames like "07 The Story of Us.m4a".

    multivalue : `bool`
        Determines whether multivalue tags are supported. If
        :code:`False`, the items in `value` are concatenated using the
        separator(s) specified in `sep`.

    sep : `str` or `tuple`, keyword-only, default: :code:`(", ", " & ")`
        Separator(s) to use to concatenate multivalue tags. If a
        :code:`str` is provided, it is used to concatenate all values.
        If a :code:`tuple` is provided, the first :code:`str` is used to
        concatenate the first :math:`n - 1` values, and the second
        :code:`str` is used to append the final value.
    """

    _CODECS = {
        "aac": {"ffmpeg": f"-b:a 256k -c:a {FFMPEG_CODECS['aac']} " "-c:v copy"},
        "alac": {"ffmpeg": "-c:a alac -c:v copy"},
    }
    _EXTENSIONS = ["m4a", "aac", "mp4"]
    _FIELDS = {
        # field: Apple iTunes metadata list key
        "album": "\xa9alb",
        "album_artist": "aART",
        "artist": "\xa9ART",
        "comment": "\xa9cmt",
        "compilation": "cpil",
        "composer": "\xa9wrt",
        "copyright": "cprt",
        "date": "\xa9day",
        "genre": "\xa9gen",
        "lyrics": "\xa9lyr",
        "tempo": "tmpo",
        "title": "\xa9nam",
    }
    _IMAGE_FORMATS = dict.fromkeys(
        ["jpg", "jpeg", "jpe", "jif", "jfif", "jfi", 13], mp4.MP4Cover.FORMAT_JPEG
    ) | dict.fromkeys(["png", 14], mp4.MP4Cover.FORMAT_PNG)

    def __init__(
        self,
        file: Union[str, pathlib.Path],
        *,
        pattern: tuple[str, tuple[str]] = None,
        multivalue: bool = False,
        sep: Union[str, list[str]] = (", ", " & "),
    ) -> None:
        """
        Create a MP4 audio file handler.
        """

        super().__init__(file, pattern=pattern, multivalue=multivalue, sep=sep)

        self._handle = mp4.MP4(file)
        self.bit_depth = self._handle.info.bits_per_sample
        self.bitrate = self._handle.info.bitrate
        self.channel_count = self._handle.info.channels
        self.codec = self._handle.info.codec
        self.sample_rate = self._handle.info.sample_rate

        self._multivalue = multivalue
        self._sep = sep
        self._from_file()
        self._from_filename()

    def _from_file(self) -> None:
        """
        Get metadata from the tags embedded in the MP4 audio file.
        """

        for field, key in self._FIELDS.items():
            value = self._handle.get(key)
            if value:
                if list not in self._FIELDS_TYPES[field]:
                    value = utility.format_multivalue(value, False, primary=True)
                    if type(value) not in self._FIELDS_TYPES[field]:
                        try:
                            value = self._FIELDS_TYPES[field][0](value)
                        except ValueError:
                            continue
                else:
                    if type(value[0]) not in self._FIELDS_TYPES[field]:
                        try:
                            value = [self._FIELDS_TYPES[field][0](v) for v in value]
                        except ValueError:
                            continue
                    if len(value) == 1:
                        value = value[0]
            else:
                value = None
            setattr(self, field, value)

        self.isrc = (
            self._handle.get("----:com.apple.iTunes:ISRC")[0].decode()
            if "----:com.apple.iTunes:ISRC" in self._handle
            else None
        )

        if "disk" in self._handle:
            self.disc_number, self.disc_count = self._handle.get("disk")[0]
        else:
            self.disc_number = self.disc_count = None

        if "trkn" in self._handle:
            self.track_number, self.track_count = self._handle.get("trkn")[0]
        else:
            self.track_number = self.track_count = None

        if "covr" in self._handle:
            self.artwork = utility.format_multivalue(
                self._handle.get("covr"), False, primary=True
            )
            self._artwork_format = (
                str(self._IMAGE_FORMATS[self.artwork.imageformat]).split(".")[1].lower()
            )
            self.artwork = bytes(self.artwork)
        else:
            self.artwork = self._artwork_format = None

    def write_metadata(self) -> None:
        """
        Write metadata to file.
        """

        for field, key in self._FIELDS.items():
            value = getattr(self, field)
            if value:
                value = utility.format_multivalue(
                    value, self._multivalue, sep=self._sep
                )
                try:
                    self._handle[key] = value
                except ValueError:
                    self._handle[key] = [value]

        if self.isrc:
            self._handle["----:com.apple.iTunes:ISRC"] = self.isrc.encode()

        if self.disc_number or self.disc_count:
            self._handle["disk"] = [(self.disc_number or 0, self.disc_count or 0)]
        if self.track_number or self.track_count:
            self._handle["trkn"] = [(self.track_number or 0, self.track_count or 0)]

        if self.artwork:
            if isinstance(self.artwork, str):
                with (
                    urllib.request.urlopen(self.artwork)
                    if "http" in self.artwork
                    else open(self.artwork, "rb")
                ) as f:
                    self.artwork = f.read()
            self._handle["covr"] = [
                mp4.MP4Cover(
                    self.artwork, imageformat=self._IMAGE_FORMATS[self._artwork_format]
                )
            ]

        self._handle.save()


class OggAudio(Audio, _VorbisComment):
    r"""
    Ogg audio file handler.

    .. seealso::

       For a full list of attributes and their descriptions, see
       :class:`Audio`.

    Parameters
    ----------
    file : `str` or `pathlib.Path`
        Ogg audio filename or path.

    codec : `str`, optional
        Audio codec. If not specified, it will be determined
        automatically.

        **Valid values**: :code:`"flac"`, :code:`"opus"`, or
        :code:`"vorbis"`.

    pattern : `tuple`, keyword-only, optional
        Regular expression search pattern and the corresponding metadata
        field(s).

        .. container::

           **Valid values**:

           The supported metadata fields are

           * :code:`"artist"` for the track artist,
           * :code:`"title"` for the track title, and
           * :code:`"track_number"` for the track number.

           **Examples**:

           * :code:`("(.*) - (.*)", ("artist", "title"))` matches
             filenames like "Taylor Swift - Blank Space.ogg".
           * :code:`("(\\d*) - (.*)", ("track_number", "title"))` matches
             filenames like "03 - Style.ogg".
           * :code:`("(\\d*) (.*)", ("track_number", "title"))` matches
             filenames like "06 Shake It Off.ogg".

    multivalue : `bool`
        Determines whether multivalue tags are supported. If
        :code:`False`, the items in `value` are concatenated using the
        separator(s) specified in `sep`.

    sep : `str` or `tuple`, keyword-only, default: :code:`(", ", " & ")`
        Separator(s) to use to concatenate multivalue tags. If a
        :code:`str` is provided, it is used to concatenate all values.
        If a :code:`tuple` is provided, the first :code:`str` is used to
        concatenate the first :math:`n - 1` values, and the second
        :code:`str` is used to append the final value.
    """

    _CODECS = {
        "flac": {"ffmpeg": "-c:a flac", "mutagen": oggflac.OggFLAC},
        "opus": {"ffmpeg": "-b:a 256k -c:a libopus -vn", "mutagen": oggopus.OggOpus},
        "vorbis": {
            "ffmpeg": f"-c:a {FFMPEG_CODECS['vorbis']} -vn",
            "mutagen": oggvorbis.OggVorbis,
        },
    }
    _EXTENSIONS = ["ogg", "oga", "opus"]

    def __init__(
        self,
        file: Union[str, pathlib.Path],
        codec: str = None,
        *,
        pattern: tuple[str, tuple[str]] = None,
        multivalue: bool = False,
        sep: Union[str, list[str]] = (", ", " & "),
    ) -> None:

        Audio.__init__(self, file, pattern=pattern, multivalue=multivalue, sep=sep)

        if codec and codec in self._CODECS:
            self.codec = codec
            self._handle = self._CODECS[codec]["mutagen"](file)
        else:
            for codec, options in self._CODECS.items():
                try:
                    self._handle = options["mutagen"](file)
                    self.codec = codec
                except Exception:
                    pass
                else:
                    break
            if not hasattr(self, "_handle"):
                raise RuntimeError(f"'{file}' is not a valid Ogg file.")
        _VorbisComment.__init__(self, self._file.name, self._handle.tags)
        self._from_filename()

        self.channel_count = self._handle.info.channels
        if self.codec == "flac":
            self.bit_depth = self._handle.info.bits_per_sample
            self.sample_rate = self._handle.info.sample_rate
            self.bitrate = self.bit_depth * self.channel_count * self.sample_rate
        elif self.codec == "opus":
            self.bit_depth = self.bitrate = self.sample_rate = None
        elif self.codec == "vorbis":
            self.bit_depth = None
            self.bitrate = self._handle.info.bitrate
            self.sample_rate = self._handle.info.sample_rate


class WAVEAudio(Audio, _ID3):
    r"""
    WAVE audio file handler.

    .. seealso::

       For a full list of attributes and their descriptions, see
       :class:`Audio`.

    Parameters
    ----------
    file : `str` or `pathlib.Path`
        WAVE audio filename or path.

    pattern : `tuple`, keyword-only, optional
        Regular expression search pattern and the corresponding metadata
        field(s).

        .. container::

           **Valid values**:

           The supported metadata fields are

           * :code:`"artist"` for the track artist,
           * :code:`"title"` for the track title, and
           * :code:`"track_number"` for the track number.

           **Examples**:

           * :code:`("(.*) - (.*)", ("artist", "title"))` matches
             filenames like "Taylor Swift - Don't Blame Me.wav".
           * :code:`("(\\d*) - (.*)", ("track_number", "title"))` matches
             filenames like "05 - Delicate.wav".
           * :code:`("(\\d*) (.*)", ("track_number", "title"))` matches
             filenames like "06 Look What You Made Me Do.wav".

    multivalue : `bool`
        Determines whether multivalue tags are supported. If
        :code:`False`, the items in `value` are concatenated using the
        separator(s) specified in `sep`.

    sep : `str` or `tuple`, keyword-only, default: :code:`(", ", " & ")`
        Separator(s) to use to concatenate multivalue tags. If a
        :code:`str` is provided, it is used to concatenate all values.
        If a :code:`tuple` is provided, the first :code:`str` is used to
        concatenate the first :math:`n - 1` values, and the second
        :code:`str` is used to append the final value.
    """

    _CODECS = {"lpcm": {"ffmpeg": "-c:a pcm_s{0:d}le -c:v copy"}}
    _EXTENSIONS = ["wav"]

    def __init__(
        self,
        file: Union[str, pathlib.Path],
        *,
        pattern: tuple[str, tuple[str]] = None,
        multivalue: bool = False,
        sep: Union[str, list[str]] = (", ", " & "),
    ) -> None:
        """
        Create a WAVE audio file handler.
        """

        _handle = wave.WAVE(file)
        if _handle.tags is None:
            _handle.add_tags()
            _handle.tags.filename = str(file)
        Audio.__init__(self, file, pattern=pattern, multivalue=multivalue, sep=sep)
        _ID3.__init__(self, self._file.name, _handle.tags)
        self._from_filename()

        self.bit_depth = _handle.info.bits_per_sample
        self.bitrate = _handle.info.bitrate
        self.channel_count = _handle.info.channels
        self.codec = "lpcm"
        self.sample_rate = _handle.info.sample_rate

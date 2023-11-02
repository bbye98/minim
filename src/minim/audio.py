"""
Audio file objects
==================
.. moduleauthor:: Benjamin Ye <GitHub: @bbye98>

This module provides convenient Python objects to keep track of audio
file handles and metadata, and convert between different audio formats.
"""

import base64
from datetime import datetime
import logging
import os
import re
import subprocess
from typing import Any, Sequence, Union
import urllib

from mutagen import id3, flac, mp3, mp4, oggopus, oggvorbis, wave

from . import utility

_ = subprocess.run(["ffmpeg", "-version"], capture_output=True)
FOUND_FFMPEG = _.returncode == 0
if not FOUND_FFMPEG:
    wmsg = ("FFmpeg was not found, so certain features in minim.audio "
            "are unavailable. To install FFmpeg, visit "
            "https://ffmpeg.org/download.html.")
    logging.warning(wmsg)
FFMPEG_AAC_CODEC = \
    "libfdk_aac" if FOUND_FFMPEG and b"--enable-libfdk-aac" in _.stdout \
    else "aac"
FFMPEG_VORBIS_CODEC = \
    "libvorbis" if FOUND_FFMPEG and b"--enable-libvorbis" in _.stdout \
    else "vorbis -strict experimental"

class _ID3:

    """
    An ID3 metadata container handler for MP3 and WAVE audio files.

    .. attention::
       This class should *not* be instantiated manually.
       Instead, use :class:`MP3Audio` or :class:`WAVEAudio` to process
       metadata for MP3 and WAVE audio files, respectively.

    Parameters
    ----------
    tags : `mutagen.id3.ID3`
        ID3 metadata.

    multivalue : `bool`
        Determines whether multivalue tags are supported (:code:`True`)
        or should be concatenated (:code:`False`) using the separator(s)
        specified in `sep`.

    sep : `str` or `tuple`
        Separator(s) to use to concatenate multivalue tags. If a 
        :code:`str` is provided, it is used to concatenate all values.
        If a :code:`tuple` is provided, the first :code:`str` is used to
        concatenate the first :math:`n - 1` values, and the second
        :code:`str` is used to append the final value.
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

    def __init__(
            self, tags: id3.ID3, multivalue: bool, 
            sep: Union[str, Sequence[str]]):
        
        """
        Create an ID3 tag handler.
        """

        self._tags = tags
        self._multivalue = multivalue
        self._sep = sep

        self._from_file()

    def _from_file(self) -> None:

        """
        Get metadata from the ID3 tags embedded in the audio file.
        """

        for field, (frame, base, _) in self._FIELDS.items():
            value = self._tags.getall(frame)
            if value: 
                value = [sv for v in value for sv in getattr(v, base)] \
                        if len(value) > 1 else getattr(value[0], base)
                if list not in self._FIELDS_TYPES[field]:
                    value = utility.multivalue_formatter(value, False, 
                                                         primary=True)
                    if type(value) not in self._FIELDS_TYPES[field]:
                        try:
                            value = self._FIELDS_TYPES[field][0](value)
                        except:
                            continue
                else:
                    if type(value[0]) not in self._FIELDS_TYPES[field]:
                        try:
                            value = [self._FIELDS_TYPES[field][0](v) 
                                     for v in value]
                        except:
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

        IMAGE_FORMATS = dict.fromkeys(
            ["jpg", "jpeg", "jpe", "jif", "jfif", "jfi"], "image/jpeg"
        ) | {"png": "image/png"}

        for field, (frame, base, func) in self._FIELDS.items():
            value = getattr(self, field)
            if value:
                value = utility.multivalue_formatter(
                    value, self._multivalue, sep=self._sep
                )
                self._tags.add(
                    getattr(id3, frame)(
                        **{base: func(value) if func else value}
                    )
                )
        
        if "TXXX:comment" in self._tags:
            self._tags.delall("TXXX:comment")

        if hasattr(self, "disc_number"):
            disc = str(self.disc_number)
            if hasattr(self, "disc_count"):
                disc += f"/{self.disc_count}"
            self._tags.add(id3.TPOS(text=disc))

        if hasattr(self, "track_number"):
            track = str(self.track_number)
            if hasattr(self, "track_count"):
                track += f"/{self.track_count}"
            self._tags.add(id3.TRCK(text=track))

        if self.artwork:
            if isinstance(self.artwork, str):
                with urllib.request.urlopen(self.artwork) \
                        if "http" in self.artwork \
                        else open(self.artwork, "rb") as f:
                    self.artwork = f.read()
            self._tags.add(
                id3.APIC(data=self.artwork, 
                         mime=IMAGE_FORMATS[self._artwork_format])
            )

        self._tags.save()

class _VorbisComment:

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
        "track_count": ("tracktotal", str)
    }

    def __init__(
            self, tags: id3.ID3, multivalue: bool, 
            sep: Union[str, Sequence[str]]):
        
        """
        Create a Vorbis comment handler.
        """

        self._tags = tags
        self._multivalue = multivalue
        self._sep = sep

        self._from_file()

    def _from_file(self) -> None:

        """
        Get metadata from the tags embedded in the FLAC audio file.
        """

        IMAGE_FILE_SIGS = {
            "jpg": b"\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01",
            "png": b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
        }

        for field, (key, _) in self._FIELDS.items():
            value = self._tags.get(key)
            if value:
                if list not in self._FIELDS_TYPES[field]:
                    value = utility.multivalue_formatter(value, False, 
                                                         primary=True)
                    if type(value) not in self._FIELDS_TYPES[field]:
                        try:
                            value = self._FIELDS_TYPES[field][0](value)
                        except:
                            continue
                else:
                    if type(value[0]) not in self._FIELDS_TYPES[field]:
                        try:
                            value = [self._FIELDS_TYPES[field][0](v) 
                                     for v in value]
                        except:
                            continue
                    if len(value) == 1:
                        value = value[0]
            else:
                value = None
            setattr(self, field, value)

        self.compilation = bool(int(self._tags.get("compilation")[0])) \
                           if "compilation" in self._tags else None
        
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

        if hasattr(self._file, "pictures") and self._file.pictures:
            self.artwork = self._file.pictures[0].data
            self._artwork_format = self._file.pictures[0].mime.split("/")[1]
        elif "metadata_block_picture" in self._tags:
            self.artwork = base64.b64decode(
                self._tags["metadata_block_picture"][0].encode()
            )
            for img_fmt, file_sig in IMAGE_FILE_SIGS.items():
                if file_sig in self.artwork:
                    self.artwork = self.artwork[
                        re.search(file_sig, self.artwork).span()[0]:
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
                value = utility.multivalue_formatter(
                    value, self._multivalue, sep=self._sep
                )
                self._tags[key] = func(value) if func else value

        if self.artwork:
            artwork = flac.Picture()
            artwork.type = id3.PictureType.COVER_FRONT
            artwork.mime = f"image/{self._artwork_format}"
            if isinstance(self.artwork, str):
                with urllib.request.urlopen(self.artwork) \
                        if "http" in self.artwork \
                        else open(self.artwork, "rb") as f:
                    self.artwork = f.read()
            artwork.data = self.artwork
            try:
                self._file.add_picture(artwork)
            except:
                self._tags["metadata_block_picture"] = base64.b64encode(
                    artwork.write()
                ).decode()

        self._file.save()

class Audio:

    """
    A generic audio file.

    Subclasses for specific audio containers or formats include
      
    * :class:`FLACAudio` for audio encoded using the Free
      Lossless Audio Codec (FLAC),
    * :class:`MP3Audio` for audio encoded and stored in the MPEG Audio
      Layer III (MP3) format,
    * :class:`MP4Audio` for audio encoded in the Advanced
      Audio Coding (AAC) format, encoded using the Apple Lossless
      Audio Codec (ALAC), or stored in a MPEG-4 Part 14 (MP4, M4A)
      container,
    * :class:`OGGAudio` for Opus or Vorbis audio stored in an Ogg file,
      or
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
    filename : `str`
        Audio filename.
      
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

    composer : `str` or `Sequence`
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
        "track_count": (int,)
    }

    def __init__(self, filename: str):
        self._filename = filename

    def __new__(cls, *args, **kwargs):

        if cls == Audio:
            filename = kwargs.get("filename")
            if filename is None:
                filename = args[0]
            if not os.path.isfile(filename):
                raise FileNotFoundError(f"'{filename}' not found.")
            
            ext = os.path.splitext(filename)[1][1:].lower()
            for a in Audio.__subclasses__():
                if ext in a._EXTENSIONS:
                    return a(*args, **kwargs)
            raise TypeError(f"'{filename}' has an unsupported audio format.")
        
        return super(Audio, cls).__new__(cls)

    def _from_filename(self, pattern: tuple[str, tuple[str]] = None) -> None:

        """
        Get track information from the filename.

        Parameters
        ----------
        pattern : `tuple`, keyword-only, optional
            Regular expression search pattern and the corresponding metadata
            field(s).
        """

        FILENAME_FIELDS = {"artist", "title", "track_number"}

        if pattern:
            groups = re.findall(pattern[0], 
                                os.path.splitext(self._filename)[0])
            if groups:
                missing = tuple(k in FILENAME_FIELDS 
                                and getattr(self, k) is None 
                                for k in pattern[1])
                for flag, attr, val in zip(missing, pattern[1], groups[0]):
                    if flag:
                        setattr(self, attr, self._FIELDS_TYPES[attr][0](val))

    def convert(
            self, codec: str, container: str = None, options: str = None, *,
            filename: str = None, preserve: bool = True) -> None:

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
                 supports Opus and Vorbis audio.
               * :code:`"wav"` or :code:`"wave"` for an WAVE audio 
                 container, which only supports LPCM audio.

        options : `str`, optional
            FFmpeg command-line options, excluding the input and output 
            files, the :code:`-y` flag (to overwrite files), and the 
            :code:`-c:v copy` argument (to preserve cover art for
            containers that support it).

            .. container::

               **Defaults**:

               * :code:`"-c:a aac -b:a 256k"` (or 
                 :code:`"-c:a libfdk_aac -b:a 256k"` if FFmpeg was
                 compiled with :code:`--enable-libfdk-aac`) for AAC 
                 audio.
               * :code:`"-c:a alac"` for ALAC audio.
               * :code:`"-c:a flac"` for FLAC audio.
               * :code:`"-c:a libmp3lame -q:a 0"` for MP3 audio.
               * :code:`"-c:a libopus -b:a 256k -vn"` for Opus audio.
               * :code:`"-c:a vorbis -strict experimental -vn"` (or 
                 :code:`"-c:a libvorbis -vn"` if FFmpeg was compiled 
                 with :code:`--enable-libvorbis`) for Vorbis audio.
               * :code:`"-c:a pcm_s16le"` or :code:`"-c:a pcm_s24le"` 
                 for WAVE audio, depending on the bit depth of the 
                 original audio file.

        filename : `str`, keyword-only, optional
            Filename of the converted audio file. If not provided, the
            filename of the original audio file, but with the 
            appropriate new extension appended, is used.

        preserve : `bool`, keyword-only, default: :code:`True`
            Determines whether the original audio file is kept.
        """

        _codec = codec.capitalize() if codec in {"opus", "vorbis"} \
                 else codec.upper()
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
                acls = next(a for a in Audio.__subclasses__() 
                            if codec in a._CODECS 
                            and container in a._EXTENSIONS)
            except:
                emsg = (f"{_codec} audio is incompatible with "
                        f"the {container.upper()} container.")
                raise RuntimeError(emsg)
        else:
            try:
                acls = next(a for a in Audio.__subclasses__() 
                            if codec in a._CODECS)
                container = acls._EXTENSIONS[0]
            except:
                raise RuntimeError(f"The '{_codec}' codec is not supported.")
    
        if not FOUND_FFMPEG:
            emsg = ("Audio conversion is unavailable because FFmpeg "
                    "was not found.")
            raise RuntimeError(emsg)
        
        if ("mp4" if codec == "aac" else codec) in self.codec \
                and isinstance(self, acls):
            wmsg = (f"'{self._filename}' already has {_codec} "
                    f"audio in a {container.upper()} container. "
                    "Re-encoding may lead to quality degradation from "
                    "generation loss.")
            logging.warning(wmsg)

        ext = f".{acls._EXTENSIONS[0]}"
        if filename is None:
            filename = (f"{os.path.splitext(self._filename)[0]}{ext}")
        else:
            if not filename.endswith(ext):
                filename += ext
            if "/" in self._filename and "/" not in filename:
                filename = f"{os.path.dirname(self._filename)}/{filename}"
        if self._filename == filename:
            filename = f"{os.path.splitext(filename)[0]}_{ext}"

        if options is None:
            if codec == "lpcm":
                options = acls._CODECS[codec]["ffmpeg"].format(
                    self.bit_depth if hasattr(self, "bit_depth") else 16
                )
            else:
                options = acls._CODECS[codec]["ffmpeg"]

        subprocess.run(
            f'ffmpeg -y -i "{self._filename}" {options} -loglevel error '
            f'-stats "{filename}"',
            shell=True
        )
        if not preserve:
            os.remove(self._filename)

        obj = acls(filename)
        self.__class__ = obj.__class__
        self.__dict__ = obj.__dict__ | {
            key: value for (key, value) in self.__dict__.items() 
            if key in self._FIELDS_TYPES
        }

    def from_itunes(
            self, data: dict, *, album_data: dict = None, 
            artwork_size: Union[int, str] = 1400, artwork_format: str = "jpg",
            overwrite: bool = False) -> None:

        """
        Populate tags using data retrieved from the iTunes Store API.
        
        .. attention::

           This method is pending a major refactor. 

        Parameters
        ----------
        data : `dict`
            Information about the track in JSON format obtained using
            the iTunes Store API via :meth:`minim.itunes.search` or
            :meth:`minim.itunes.lookup`.

        album_data : `dict`, keyword-only, optional
            Information about the track's album in JSON format obtained
            using the iTunes Store API via :meth:`minim.itunes.search`
            or :meth:`minim.itunes.lookup`. If not provided, album 
            artist and copyright information is unavailable.

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
                            f"/{re.search(r'Feature.*?(png|jpg)(?=/|$)', self.artwork)[0]}"
                        )
                    elif "Music" in self.artwork:
                        self.artwork = (
                            "https://a5.mzstatic.com/"
                            f"{re.search(r'Music.*?(png|jpg)(?=/|$)', self.artwork)[0]}"
                        )
                    self._artwork_format = os.path.splitext(self.artwork)[-1][1:]
                else:
                    self.artwork = self.artwork.replace(
                        "100x100bb.jpg",
                        f"{artwork_size}x{artwork_size}bb.{artwork_format}"
                    )
                    self._artwork_format = artwork_format
                with urllib.request.urlopen(self.artwork) as r:
                    self.artwork = r.read()
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

    def from_spotify(
            self, data: dict, *, audio_features: dict[str, Any] = None,
            lyrics: Union[str, dict[str, Any]] = None, overwrite: bool = False
        ) -> None:

        """
        Populate tags using data retrieved from the Spotify Web API.

        .. attention::

           This method is pending a major refactor.

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
            lyrics obtained using the Spotify Lyrics API via 
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
            self.lyrics = lyrics if isinstance(lyrics, str) \
                          else "\n".join(l["words"] 
                                         for l in lyrics["lyrics"]["lines"])
        if (self.tempo is None or overwrite) and audio_features:
            self.tempo = round(audio_features["tempo"])
        if self.title is None or overwrite:
            self.title = data["name"]
        if self.track_number is None or overwrite:
            self.track_number = data["track_number"]
        if self.track_count is None or overwrite:
            self.track_count = data["album"]["total_tracks"]

    def from_tidal(
            self, data: dict, *, album_data: dict = None,
            composer: Union[str, list[str]] = None, artwork: bytes = None,
            lyrics: dict[str, Any] = None, comment: str = None,
            overwrite: bool = False) -> None:
        
        """
        Populate tags using data retrieved from the private TIDAL API.

        .. attention::

           This method is pending a major refactor. 

        Parameters
        ----------
        data : `dict`
            Information about the track in JSON format obtained using
            the TIDAL API via :meth:`minim.tidal.PrivateAPI.get_track`.

        album_data : `dict`, keyword-only, optional
            Information about the track's album in JSON format obtained
            using the TIDAL API via 
            :meth:`minim.tidal.PrivateAPI.get_album`. If not provided, 
            album artist, copyright, and disc and track numbering 
            information is unavailable.
        
        composer : `str` or `list`, keyword-only, optional
            Information about the track's composers obtained using the
            TIDAL API via 
            :meth:`minim.tidal.PrivateAPI.get_track_composers`. If not 
            provided, songwriting credits are unavailable.

        artwork : `str`, keyword-only, optional
            TIDAL URL of the track cover art obtained using the TIDAL
            API via :meth:`minim.tidal.PrivateAPI.get_image`.

        lyrics : `str` or `dict`, keyword-only, optional
            The track's lyrics obtained using the TIDAL API via
            :meth:`minim.tidal.PrivateAPI.get_track_lyrics`.

        comment : `str`, keyword-only, optional
            Comment or description.

        overwrite : `bool`, keyword-only, default: :code:`False`
            Determines whether existing metadata should be overwritten.
        """

        if self.album is None or overwrite:
            self.album = data["album"]["title"]
        if self.artist is None or overwrite:
            self.artist = [a["name"] for a in data["artists"] 
                           if a["type"] == "MAIN"]
        if (self.artwork is None or overwrite) and artwork:
            self.artwork = artwork
            self._artwork_format = os.path.splitext(artwork)[1][1:]
        if (self.comment is None or overwrite) and comment:
            self.comment = comment
        if (self.composer is None or overwrite) and composer:
            self.composer = composer
        if self.date is None or overwrite:
            self.date = data["streamStartDate"].split(".")[0]
        if self.disc_number is None or overwrite:
            self.disc_number = data["volumeNumber"]
        if self.isrc is None or overwrite:
            self.isrc = data["isrc"]
        if (self.lyrics is None or overwrite) and lyrics:
            self.lyrics = lyrics if isinstance(lyrics, str) \
                          else lyrics["lyrics"]
        if self.title is None or overwrite:
            self.title = data["title"]
        if self.track_number is None or overwrite:
            self.track_number = data["trackNumber"]
    
        if album_data:
            if self.album_artist is None or overwrite:
                self.album_artist = [a["name"] for a in album_data["artists"] 
                                     if a["type"] == "MAIN"]
            if self.copyright is None or overwrite:
                self.copyright = album_data["copyright"]
            if self.disc_count is None or overwrite:
                self.disc_count = album_data["numberOfVolumes"]
            if self.track_count is None or overwrite:
                self.track_count = album_data["numberOfTracks"]

    def from_qobuz(
            self, data: dict, main_artist: Union[str, list[str]] = None,
            feat_artist: Union[str, list[str]] = None,
            composer: Union[str, list[str]] = None, artwork: bytes = None,
            comment: str = None, overwrite: bool = False) -> None:

        """
        Populate tags using data retrieved from the Qobuz API.

        .. attention::

           This method is pending a major refactor.

        Parameters
        ----------
        data : `dict`
            Information about the track in JSON format obtained using
            the Qobuz API via :meth:`minim.qobuz.PrivateAPI.get_track`.

        main_artist : `str` or `list`, keyword-only, optional
            Information about the track's main artists obtained using 
            the Qobuz API via :meth:`minim.qobuz.PrivateAPI.get_track` 
            and/or :meth:`minim.qobuz.PrivateAPI.get_track_credits`. If not 
            provided, only information about the primary artist will be
            available.

        feat_artist : `str` or `list`, keyword-only, optional
            Information about the track's featured artists obtained 
            using the Qobuz API via :meth:`minim.qobuz.PrivateAPI.get_track` 
            and/or :meth:`minim.qobuz.PrivateAPI.get_track_credits`. If not 
            provided, the featured artists will not be listed in the 
            track's title.

        composer : `str` or `list`, keyword-only, optional
            Information about the track's composers obtained using the
            Qobuz API via :meth:`minim.qobuz.PrivateAPI.get_track` and/or 
            :meth:`minim.qobuz.PrivateAPI.get_track_credits`. If not 
            provided, songwriting credits are unavailable.

        artwork : `str`, keyword-only, optional
            Qobuz URL of the track cover art obtained using the Qobuz
            API via :meth:`minim.qobuz.PrivateAPI.get_track`.

        comment : `str`, keyword-only, optional
            Comment or description.

        overwrite : `bool`, keyword-only, default: :code:`False`
            Determines whether existing metadata should be overwritten.
        """

        if self.album is None or overwrite:
            self.album = data["album"]["title"].rstrip()
            feat_album_artist = [a["name"] for a in data["album"]["artists"]
                                 if "featured-artist" in a["roles"]]
            if feat_album_artist and "feat." not in self.album:
                self.album += (" [feat. {}]" if "(" in self.album 
                               else " (feat. {})").format(
                    utility.multivalue_formatter(feat_album_artist, False)
                )
            if data["album"]["version"]:
                self.album += (" [{}]" if "(" in self.album 
                               else " ({})").format(
                    data['album']['version']
                )
        if self.album_artist is None or overwrite:
            album_artist = [a["name"] for a in data["album"]["artists"] 
                            if "main-artist" in a["roles"]]
            main_album_artist = data["album"]["artist"]["name"]
            if main_album_artist in album_artist:
                i = album_artist.index(main_album_artist) \
                    if main_album_artist in album_artist else 0
                if i != 0:
                    album_artist.insert(0, album_artist.pop(i))
                self.album_artist = album_artist
            else:
                self.album_artist = main_album_artist
        if self.artist is None or overwrite:
            self.artist = main_artist if main_artist \
                          else data["performer"]["name"]
        if (self.artwork is None or overwrite) and artwork:
            self.artwork = artwork
            self._artwork_format = os.path.splitext(artwork)[1][1:]
        if self.comment is None or overwrite:
            self.comment = comment
        if (self.composer is None or overwrite) and composer:
            self.composer = composer
        if self.copyright is None or overwrite:
            self.copyright = data["album"]["copyright"]
        if self.date is None or overwrite:
            self.date = datetime.utcfromtimestamp(
                min(
                    data.get(k) if k in data and data.get(k) 
                    else 2 ** 31 - 1 for k in {
                        "release_date_original", 
                        "release_date_download", 
                        "release_date_stream", 
                        "purchasable_at", 
                        "streamable_at"
                    }
                )
            ).strftime('%Y-%m-%dT%H:%M:%SZ')
        if self.disc_number is None or overwrite:
            self.disc_number = data["media_number"]
        if self.disc_count is None or overwrite:
            self.disc_count = data["album"]["media_count"]
        if self.genre is None or overwrite:
            self.genre = data["album"]["genre"]["name"]
        if self.isrc is None or overwrite:
            self.isrc = data["isrc"]
        if self.title is None or overwrite:
            self.title = data["title"].rstrip()
            if feat_artist and "feat." not in self.title:
                self.title += (" [feat. {}]" if "(" in self.title 
                               else " (feat. {})").format(
                    utility.multivalue_formatter(feat_artist, False)
                )
            if data["version"]:
                self.title += (" [{}]" if "(" in self.title 
                               else " ({})").format(data['version'])
        if self.track_number is None or overwrite:
            self.track_number = data["track_number"]
        if self.track_count is None or overwrite:
            self.track_count = data["album"]["tracks_count"]

        if data["album"]["product_type"] == "single" \
                and self.album == self.title:
            self.album += " - Single"
            self.album_artist = self.artist = max(self.artist, 
                                                  self.album_artist, 
                                                  key=len)

class FLACAudio(Audio, _VorbisComment):

    """
    A FLAC audio file.

    Parameters
    ----------
    filename : `str`
        FLAC audio filename.

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
           * :code:`("(.*) - (.*)", ("track_number", "title"))` matches
             filenames like "03 - Love Story.flac".
           * :code:`("(\d*) (.*)", ("track_number", "title"))` matches
             filenames like "06 You Belong with Me.flac".

    multivalue : `bool`, keyword-only, default: :code:`False`
        Determines whether multivalue tags are supported (:code:`True`)
        or should be concatenated (:code:`False`) using the separator(s)
        specified in `sep`.

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
            self, filename: str, *, pattern: tuple[str, tuple[str]] = None,
            multivalue: bool = False, 
            sep: Union[str, Sequence[str]] = (", ", " & ")):

        """
        Create a FLAC audio file handler.
        """

        Audio.__init__(self, filename)

        self._file = flac.FLAC(filename)
        if self._file.tags is None:
            self._file.add_tags()
        _VorbisComment.__init__(self, self._file.tags, multivalue, sep)

        self.bit_depth = self._file.info.bits_per_sample
        self.bitrate = self._file.info.bitrate
        self.channel_count = self._file.info.channels
        self.codec = "flac"
        self.sample_rate = self._file.info.sample_rate

        self._from_filename(pattern)

class MP3Audio(Audio, _ID3):

    """
    An MP3 audio file.

    Parameters
    ----------
    filename : `str`
        MP3 audio filename.

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
           * :code:`("(.*) - (.*)", ("track_number", "title"))` matches
             filenames like "04 - I Knew You Were Trouble.mp3".
           * :code:`("(\d*) (.*)", ("track_number", "title"))` matches
             filenames like "06 22.mp3".

    multivalue : `bool`, keyword-only, default: :code:`False`
        Determines whether multivalue tags are supported (:code:`True`)
        or should be concatenated (:code:`False`) using the separator(s)
        specified in `sep`.

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
            self, filename: str, *, pattern: tuple[str, tuple[str]] = None,
            multivalue: bool = False,
            sep: Union[str, Sequence[str]] = (", ", " & ")):

        """
        Create a MP3 audio file handler.
        """

        file = mp3.MP3(filename)
        file.tags.filename = filename
        Audio.__init__(self, filename)
        _ID3.__init__(self, file.tags, multivalue, sep)

        self.bit_depth = None
        self.bitrate = file.info.bitrate
        self.channel_count = file.info.channels
        self.codec = "mp3"
        self.sample_rate = file.info.sample_rate

        self._from_filename(pattern)

class MP4Audio(Audio):

    """
    An MP4 audio file.

    Parameters
    ----------
    filename : `str`
        MP4 audio filename.

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
           * :code:`("(.*) - (.*)", ("track_number", "title"))` matches
             filenames like "04 - Speak Now.m4a".
           * :code:`("(\d*) (.*)", ("track_number", "title"))` matches
             filenames like "07 The Story of Us.m4a".

    multivalue : `bool`, keyword-only, default: :code:`False`
        Determines whether multivalue tags are supported (:code:`True`)
        or should be concatenated (:code:`False`) using the separator(s)
        specified in `sep`.

    sep : `str` or `tuple`, keyword-only, default: :code:`(", ", " & ")`
        Separator(s) to use to concatenate multivalue tags. If a 
        :code:`str` is provided, it is used to concatenate all values.
        If a :code:`tuple` is provided, the first :code:`str` is used to
        concatenate the first :math:`n - 1` values, and the second
        :code:`str` is used to append the final value.
    """

    _CODECS = {"aac": {"ffmpeg": f"-b:a 256k -c:a {FFMPEG_AAC_CODEC} "
                                 "-c:v copy"},
               "alac": {"ffmpeg": "-c:a alac -c:v copy"}}
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
        ["jpg", "jpeg", "jpe", "jif", "jfif", "jfi", 13],
        mp4.MP4Cover.FORMAT_JPEG
    ) | dict.fromkeys(["png", 14], mp4.MP4Cover.FORMAT_PNG)

    def __init__(
            self, filename: str, *, pattern: tuple[str, tuple[str]] = None,
            multivalue: bool = False,
            sep: Union[str, Sequence[str]] = (", ", " & ")):
        
        """
        Create a MP4 audio file handler.
        """
        
        super().__init__(filename)

        self._tags = mp4.MP4(filename)
        self.bit_depth = self._tags.info.bits_per_sample
        self.bitrate = self._tags.info.bitrate
        self.channel_count = self._tags.info.channels
        self.codec = self._tags.info.codec
        self.sample_rate = self._tags.info.sample_rate
        self._multivalue = multivalue
        self._sep = sep

        self._from_file()
        self._from_filename(pattern)

    def _from_file(self) -> None:

        """
        Get metadata from the tags embedded in the MP4 audio file.
        """

        for field, key in self._FIELDS.items():
            value = self._tags.get(key)
            if value:
                if list not in self._FIELDS_TYPES[field]:
                    value = utility.multivalue_formatter(value, False, 
                                                         primary=True)
                    if type(value) not in self._FIELDS_TYPES[field]:
                        try:
                            value = self._FIELDS_TYPES[field][0](value)
                        except:
                            continue
                else:
                    if type(value[0]) not in self._FIELDS_TYPES[field]:
                        try:
                            value = [self._FIELDS_TYPES[field][0](v) 
                                     for v in value]
                        except:
                            continue
                    if len(value) == 1:
                        value = value[0]
            else:
                value = None
            setattr(self, field, value)

        self.isrc = self._tags.get("----:com.apple.iTunes:ISRC")[0].decode() \
                    if "----:com.apple.iTunes:ISRC" in self._tags else None

        if "disk" in self._tags:
            self.disc_number, self.disc_count = self._tags.get("disk")[0]
        else:
            self.disc_number = self.disc_count = None
            
        if "trkn" in self._tags:
            self.track_number, self.track_count = self._tags.get("trkn")[0]
        else:
            self.track_number = self.track_count = None

        if "covr" in self._tags:
            self.artwork = utility.multivalue_formatter(self._tags.get("covr"), 
                                                        False, primary=True)
            self._artwork_format = str(
                self._IMAGE_FORMATS[self.artwork.imageformat]
            ).split(".")[1].lower()
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
                value = utility.multivalue_formatter(
                    value, self._multivalue, sep=self._sep
                )
                try:
                    self._tags[key] = value
                except:
                    self._tags[key] = [value]

        if self.isrc:
            self._tags["----:com.apple.iTunes:ISRC"] = self.isrc.encode()

        if self.disc_number or self.disc_count:
            self._tags["disk"] = [(self.disc_number or 0, 
                                   self.disc_count or 0)]
        if self.track_number or self.track_count:
            self._tags["trkn"] = [(self.track_number or 0, 
                                   self.track_count or 0)]
        
        if self.artwork:
            if isinstance(self.artwork, str):
                with urllib.request.urlopen(self.artwork) \
                        if "http" in self.artwork \
                        else open(self.artwork, "rb") as f:
                    self.artwork = f.read()
            self._tags["covr"] = [
                mp4.MP4Cover(
                    self.artwork, 
                    imageformat=self._IMAGE_FORMATS[self._artwork_format]
                )
            ]

        self._tags.save()

class OGGAudio(Audio, _VorbisComment):

    """
    An OGG audio file.

    Parameters
    ----------
    filename : `str`
        WAVE audio filename.

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
           * :code:`("(.*) - (.*)", ("track_number", "title"))` matches
             filenames like "03 - Style.ogg".
           * :code:`("(\d*) (.*)", ("track_number", "title"))` matches
             filenames like "06 Shake It Off.ogg".

    multivalue : `bool`, keyword-only, default: :code:`False`
        Determines whether multivalue tags are supported (:code:`True`)
        or should be concatenated (:code:`False`) using the separator(s)
        specified in `sep`.

    sep : `str` or `tuple`, keyword-only, default: :code:`(", ", " & ")`
        Separator(s) to use to concatenate multivalue tags. If a 
        :code:`str` is provided, it is used to concatenate all values.
        If a :code:`tuple` is provided, the first :code:`str` is used to
        concatenate the first :math:`n - 1` values, and the second
        :code:`str` is used to append the final value.
    """

    _CODECS = {"opus": {"ffmpeg": "-b:a 256k -c:a libopus -vn", 
                        "mutagen": oggopus.OggOpus},
               "vorbis": {"ffmpeg": f"-c:a {FFMPEG_VORBIS_CODEC} -vn",
                          "mutagen": oggvorbis.OggVorbis}
            }
    _EXTENSIONS = ["ogg", "oga", "opus"]

    def __init__(
            self, filename: str, codec: str = None, *, 
            pattern: tuple[str, tuple[str]] = None, multivalue: bool = False,
            sep: Union[str, Sequence[str]] = (", ", " & ")):
        
        Audio.__init__(self, filename)

        if codec and codec in self._CODECS:
            self.codec = codec
            self._file = self._CODECS[codec]["mutagen"](filename)
        else:
            for codec, options in self._CODECS.items():
                try:
                    self._file = options["mutagen"](filename)
                    self.codec = codec
                    break
                except:
                    pass

        if not hasattr(self, "_file"):
            raise RuntimeError(f"'{filename}' is not a valid Ogg file.")

        self._tags = self._file.tags
        _VorbisComment.__init__(self, self._file.tags, multivalue, sep)

        self.channel_count = self._file.info.channels
        if self.codec == "flac":
            self.bit_depth = self._file.info.bits_per_sample
            self.sample_rate = self._file.info.sample_rate 
            self.bitrate = self.bit_depth * self.channel_count \
                           * self.sample_rate
        elif self.codec == "opus":
            self.bit_depth = self.bitrate = self.sample_rate = None
        elif self.codec == "vorbis":
            self.bit_depth = None
            self.bitrate = self._file.info.bitrate
            self.sample_rate = self._file.info.sample_rate

        self._from_filename(pattern)

class WAVEAudio(Audio, _ID3):

    """
    A WAVE audio file.

    Parameters
    ----------
    filename : `str`
        WAVE audio filename.

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
           * :code:`("(.*) - (.*)", ("track_number", "title"))` matches
             filenames like "05 - Delicate.wav".
           * :code:`("(\d*) (.*)", ("track_number", "title"))` matches
             filenames like "06 Look What You Made Me Do.wav".

    multivalue : `bool`, keyword-only, default: :code:`False`
        Determines whether multivalue tags are supported (:code:`True`)
        or should be concatenated (:code:`False`) using the separator(s)
        specified in `sep`.

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
            self, filename: str, *, pattern: tuple[str, tuple[str]] = None,
            multivalue: bool = False,
            sep: Union[str, Sequence[str]] = (", ", " & ")):

        """
        Create a WAV audio file handler.
        """

        file = wave.WAVE(filename)
        if file.tags is None:
            file.add_tags()
            file.tags.filename = file.filename
        Audio.__init__(self, filename)
        _ID3.__init__(self, file.tags, multivalue, sep)

        self.bit_depth = file.info.bits_per_sample
        self.bitrate = file.info.bitrate
        self.channel_count = file.info.channels
        self.codec = "lpcm"
        self.sample_rate = file.info.sample_rate

        self._from_filename(pattern)
from copy import copy
import os
from pathlib import Path
import sys

sys.path.insert(0, f"{Path(__file__).parents[1].resolve()}/src")
from minim import audio  # noqa: E402


class TestAudio:

    @classmethod
    def setup_class(cls):
        cls.obj = audio.Audio(Path(__file__).parent / "data/samples/middle_c.wav")
        assert isinstance(cls.obj, audio.WAVEAudio)

    def test_convert_flac(self):
        self.obj_new = copy(self.obj)
        self.obj_new.convert("flac", filename="middle_c_flac")
        assert (
            isinstance(self.obj_new, audio.FLACAudio)
            and self.obj.bit_depth == self.obj_new.bit_depth
            and self.obj_new.codec == "flac"
            and self.obj.sample_rate == self.obj_new.sample_rate
        )

        self.obj_new.title = "Middle C (Copy)"
        self.obj_new.write_metadata()
        self.obj_new = audio.FLACAudio(self.obj_new._file)
        assert self.obj_new.title == "Middle C (Copy)"
        os.remove(self.obj_new._file)

    def test_convert_mp3(self):
        self.obj_new = copy(self.obj)
        self.obj_new.convert("mp3", filename="middle_c_mp3")
        assert isinstance(self.obj_new, audio.MP3Audio) and self.obj_new.codec == "mp3"

        self.obj_new.title = "Middle C (Copy)"
        self.obj_new.write_metadata()
        self.obj_new = audio.MP3Audio(self.obj_new._file)
        assert self.obj_new.title == "Middle C (Copy)"
        os.remove(self.obj_new._file)

    def test_convert_mp4_aac(self):
        self.obj_new = copy(self.obj)
        self.obj_new.convert("aac", filename="middle_c_aac")
        assert isinstance(self.obj_new, audio.MP4Audio) and "mp4a" in self.obj_new.codec

        self.obj_new.title = "Middle C (Copy)"
        self.obj_new.write_metadata()
        self.obj_new = audio.MP4Audio(self.obj_new._file)
        assert self.obj_new.title == "Middle C (Copy)"
        os.remove(self.obj_new._file)

    def test_convert_mp4_alac(self):
        self.obj_new = copy(self.obj)
        self.obj_new.convert("alac", filename="middle_c_alac")
        assert (
            isinstance(self.obj_new, audio.MP4Audio)
            and self.obj.bit_depth == self.obj_new.bit_depth
            and self.obj_new.codec == "alac"
            and self.obj.sample_rate == self.obj_new.sample_rate
        )

        self.obj_new.title = "Middle C (Copy)"
        self.obj_new.write_metadata()
        self.obj_new = audio.MP4Audio(self.obj_new._file)
        assert self.obj_new.title == "Middle C (Copy)"
        os.remove(self.obj_new._file)

    def test_convert_ogg_flac(self):
        self.obj_new = copy(self.obj)
        self.obj_new.convert("flac", "ogg", filename="middle_c_flac")
        assert (
            isinstance(self.obj_new, audio.OggAudio)
            and self.obj.bit_depth == self.obj_new.bit_depth
            and self.obj_new.codec == "flac"
            and self.obj.sample_rate == self.obj_new.sample_rate
        )

        self.obj_new.title = "Middle C (Copy)"
        self.obj_new.write_metadata()
        self.obj_new = audio.OggAudio(self.obj_new._file)
        assert self.obj_new.title == "Middle C (Copy)"
        os.remove(self.obj_new._file)

    def test_convert_ogg_opus(self):
        self.obj_new = copy(self.obj)
        self.obj_new.convert("opus", filename="middle_c_opus")
        assert isinstance(self.obj_new, audio.OggAudio) and self.obj_new.codec == "opus"

        self.obj_new.title = "Middle C (Copy)"
        self.obj_new.write_metadata()
        self.obj_new = audio.OggAudio(self.obj_new._file)
        assert self.obj_new.title == "Middle C (Copy)"
        os.remove(self.obj_new._file)

    def test_convert_ogg_vorbis(self):
        self.obj_new = copy(self.obj)
        self.obj_new.convert("vorbis", filename="middle_c_vorbis")
        assert (
            isinstance(self.obj_new, audio.OggAudio) and self.obj_new.codec == "vorbis"
        )

        self.obj_new.title = "Middle C (Copy)"
        self.obj_new.write_metadata()
        self.obj_new = audio.OggAudio(self.obj_new._file)
        assert self.obj_new.title == "Middle C (Copy)"
        os.remove(self.obj_new._file)

    def test_convert_wave_16bit(self):
        self.obj_new = copy(self.obj)
        self.obj_new.convert("wav", filename="middle_c_16bit", options="-c:a pcm_s16le")
        assert isinstance(self.obj_new, audio.WAVEAudio)

        self.obj_new.title = "Middle C (Copy)"
        self.obj_new.write_metadata()
        self.obj_new = audio.WAVEAudio(self.obj_new._file)
        assert self.obj_new.title == "Middle C (Copy)"
        os.remove(self.obj_new._file)

from pathlib import Path
import sys

sys.path.insert(0, f"{Path(__file__).parents[1]}/src")
from minim import discogs # noqa: E402

class TestAPI:

    @classmethod
    def setup_class(cls):
        cls.obj = discogs.API()
import pathlib
import sys

sys.path.insert(0, f"{pathlib.Path(__file__).parents[1].resolve()}/src")
from minim import qobuz

class TestPrivateAPI:

    ALBUM_ID = "0060254735180"
    ARTIST_ID = 594172
    LABEL_ID = 1153
    PLAYLIST_ID = 15732665
    TRACK_ID = 24393138

    @classmethod
    def setup_class(cls):
        cls.obj = qobuz.PrivateAPI()

    def test_get_album(self):
        assert self.obj.get_album(self.ALBUM_ID)["id"] == self.ALBUM_ID

    def test_get_featured_albums(self):
        assert "albums" in self.obj.get_featured_albums()

    def test_get_artist(self):
        assert self.obj.get_artist(self.ARTIST_ID)["id"] == self.ARTIST_ID

    def test_get_label(self):
        assert self.obj.get_label(self.LABEL_ID)["id"] == self.LABEL_ID

    def test_get_playlist(self):
        assert self.obj.get_playlist(self.PLAYLIST_ID)["id"] == self.PLAYLIST_ID

    def test_get_featured_playlists(self):
        assert all("is_collaborative" in p 
                   for p in self.obj.get_featured_playlists()["items"])

    def test_search(self):
        query = "zedd true colors"
        assert self.obj.search(query)["query"] == query

    def test_get_track(self):
        assert self.obj.get_track(self.TRACK_ID)["id"] == self.TRACK_ID

    def test_get_track_credits(self):
        assert isinstance(self.obj.get_track_credits(self.TRACK_ID), dict)
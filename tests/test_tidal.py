from pathlib import Path
import sys

sys.path.insert(0, f"{Path(__file__).parents[1]}/src")
from minim import tidal

class TestAPI:

    ALBUM_IDS = ["251380836", "275646830"]
    ALBUM_BARCODE_ID = "196589525444"
    ARTIST_IDS = ["1566", "7804"]
    TRACK_IDS = ["251380837", "251380838"]
    VIDEO_IDS = ["59727844", "75623239"]

    @classmethod
    def setup_class(cls):
        cls.obj = tidal.API()

    def test_get_album(self):
        album = self.obj.get_album(self.ALBUM_IDS[0], "US")
        assert album["id"] == self.ALBUM_IDS[0]

    def test_get_albums(self):
        albums = self.obj.get_albums(self.ALBUM_IDS, "US")
        assert all(a["resource"]["id"] == i 
                   for a, i in zip(albums["data"], self.ALBUM_IDS))

    def test_get_album_items(self):
        items = self.obj.get_album_items(self.ALBUM_IDS[0], "US")
        assert all(i["resource"]["album"]["id"] == self.ALBUM_IDS[0]
                   for i in items["data"])
        
    def test_get_album_by_barcode_id(self):
        album = self.obj.get_album_by_barcode_id(self.ALBUM_BARCODE_ID, "US")
        assert (album["data"][0]["resource"]["barcodeId"] 
                == self.ALBUM_BARCODE_ID)
        
    def test_get_artist(self):
        artist = self.obj.get_artist(self.ARTIST_IDS[0], "US")
        assert artist["id"] == self.ARTIST_IDS[0]

    def test_get_artists(self):
        artists = self.obj.get_artists(self.ARTIST_IDS, "US")
        assert all(a["resource"]["id"] == i 
                   for a, i in zip(artists["data"], self.ARTIST_IDS))
        
    def test_get_artist_albums(self):
        albums = self.obj.get_artist_albums(self.ARTIST_IDS[0], "US")
        assert all(a["resource"]["artists"][0]["id"] == self.ARTIST_IDS[0]
                   for a in albums["data"])
        
    def test_get_track(self):
        track = self.obj.get_track(self.TRACK_IDS[0], "US")
        assert track["id"] == self.TRACK_IDS[0]

    def test_get_tracks(self):
        tracks = self.obj.get_tracks(self.TRACK_IDS, "US")
        assert all(t["resource"]["id"] == i 
                   for t, i in zip(tracks["data"], self.TRACK_IDS))
        
    def test_get_video(self):
        video = self.obj.get_video(self.VIDEO_IDS[0], "US")
        assert video["id"] == self.VIDEO_IDS[0]

    def test_get_videos(self):
        videos = self.obj.get_videos(self.VIDEO_IDS, "US")
        assert all(v["resource"]["id"] == i 
                   for v, i in zip(videos["data"], self.VIDEO_IDS))
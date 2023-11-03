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
        
class TestPrivateAPI:

    ALBUM_IDS = [251380836, 275646830]
    ARTIST_IDS = [1566, 7804]
    MIX_UUIDs = ["000ec0b01da1ddd752ec5dee553d48",
                 "000dd748ceabd5508947c6a5d3880a"]
    PLAYLIST_UUIDS = ["36ea71a8-445e-41a4-82ab-6628c581535d",
                      "4261748a-4287-4758-aaab-6d5be3e99e52"]
    TRACK_IDS = [251380837, 251380838]
    VIDEO_IDS = [59727844, 75623239]

    @classmethod
    def setup_class(cls):
        cls.obj = tidal.PrivateAPI()

    def test_get_album(self):
        album = self.obj.get_album(self.ALBUM_IDS[0])
        assert album["id"] == self.ALBUM_IDS[0]

    def test_get_album_items(self):
        items = self.obj.get_album_items(self.ALBUM_IDS[0])["items"]
        assert all(i["item"]["album"]["id"] == self.ALBUM_IDS[0] 
                   for i in items)

    def test_get_artist(self):
        artist = self.obj.get_artist(self.ARTIST_IDS[0])
        assert artist["id"] == self.ARTIST_IDS[0]

    def test_get_artist_albums(self):
        albums = self.obj.get_artist_albums(self.ARTIST_IDS[0])["items"]
        assert all(a["artist"]["id"] == self.ARTIST_IDS[0]
                   for a in albums)
        
    def test_get_artist_top_tracks(self):
        tracks = self.obj.get_artist_top_tracks(self.ARTIST_IDS[0])
        assert all(self.ARTIST_IDS[0] in (a["id"] for a in t["artists"])
                   for t in tracks["items"])

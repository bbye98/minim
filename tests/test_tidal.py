from pathlib import Path
import sys

sys.path.insert(0, f"{Path(__file__).parents[1]}/src")
from minim import tidal  # noqa: E402

# class TestAPI:

#     ALBUM_IDS = ["251380836", "275646830"]
#     ALBUM_BARCODE_ID = "196589525444"
#     ARTIST_IDS = ["1566", "7804"]
#     TRACK_IDS = ["251380837", "251380838"]
#     VIDEO_IDS = ["59727844", "75623239"]

#     @classmethod
#     def setup_class(cls):
#         cls.obj = tidal.API()

#     def test_get_album(self):
#         album = self.obj.get_album(self.ALBUM_IDS[0], "US")
#         assert album["id"] == self.ALBUM_IDS[0]

#     def test_get_albums(self):
#         albums = self.obj.get_albums(self.ALBUM_IDS, "US")
#         assert all(a["resource"]["id"] == i
#                    for a, i in zip(albums["data"], self.ALBUM_IDS))

#     def test_get_album_items(self):
#         items = self.obj.get_album_items(self.ALBUM_IDS[0], "US")
#         assert all(i["resource"]["album"]["id"] == self.ALBUM_IDS[0]
#                    for i in items["data"])

#     def test_get_album_by_barcode_id(self):
#         album = self.obj.get_album_by_barcode_id(self.ALBUM_BARCODE_ID, "US")
#         assert (album["data"][0]["resource"]["barcodeId"]
#                 == self.ALBUM_BARCODE_ID)

#     def test_get_artist(self):
#         artist = self.obj.get_artist(self.ARTIST_IDS[0], "US")
#         assert artist["id"] == self.ARTIST_IDS[0]

#     def test_get_artists(self):
#         artists = self.obj.get_artists(self.ARTIST_IDS, "US")
#         assert all(a["resource"]["id"] == i
#                    for a, i in zip(artists["data"], self.ARTIST_IDS))

#     def test_get_artist_albums(self):
#         albums = self.obj.get_artist_albums(self.ARTIST_IDS[0], "US")
#         assert all(a["resource"]["artists"][0]["id"] == self.ARTIST_IDS[0]
#                    for a in albums["data"])

#     def test_get_track(self):
#         track = self.obj.get_track(self.TRACK_IDS[0], "US")
#         assert track["id"] == self.TRACK_IDS[0]

#     def test_get_tracks(self):
#         tracks = self.obj.get_tracks(self.TRACK_IDS, "US")
#         assert all(t["resource"]["id"] == i
#                    for t, i in zip(tracks["data"], self.TRACK_IDS))

#     def test_get_video(self):
#         video = self.obj.get_video(self.VIDEO_IDS[0], "US")
#         assert video["id"] == self.VIDEO_IDS[0]

#     def test_get_videos(self):
#         videos = self.obj.get_videos(self.VIDEO_IDS, "US")
#         assert all(v["resource"]["id"] == i
#                    for v, i in zip(videos["data"], self.VIDEO_IDS))


class TestPrivateAPI:

    ALBUM_ID = 251380836
    ARTIST_ID = 1566
    MIX_UUID = "000ec0b01da1ddd752ec5dee553d48"
    PLAYLIST_UUID = "36ea71a8-445e-41a4-82ab-6628c581535d"
    TRACK_ID = 251380837
    VIDEO_ID = 59727844

    @classmethod
    def setup_class(cls):
        cls.obj = tidal.PrivateAPI()

    def test_get_album(self):
        album = self.obj.get_album(self.ALBUM_ID)
        assert album["id"] == self.ALBUM_ID

    def test_get_album_items(self):
        assert all(
            i["item"]["album"]["id"] == self.ALBUM_ID
            for i in self.obj.get_album_items(self.ALBUM_ID)["items"]
        )

    def test_get_album_credits(self):
        assert all(
            k in c
            for c in self.obj.get_album_credits(self.ALBUM_ID)
            for k in {"type", "contributors"}
        )

    def test_get_album_review(self):
        assert all(
            k in self.obj.get_album_review(self.ALBUM_ID)
            for k in {"source", "lastUpdated", "text", "summary"}
        )

    def test_get_similar_albums(self):
        assert all(
            a["type"] in {"ALBUM", "SINGLE"}
            for a in self.obj.get_similar_albums(self.ALBUM_ID)["items"]
        )

    def test_get_artist(self):
        assert self.obj.get_artist(self.ARTIST_ID)["id"] == self.ARTIST_ID

    def test_get_artist_albums(self):
        assert all(
            self.ARTIST_ID in (a["id"] for a in c["artists"])
            for c in self.obj.get_artist_albums(self.ARTIST_ID)["items"]
        )

    def test_get_artist_top_tracks(self):
        assert all(
            self.ARTIST_ID in (a["id"] for a in t["artists"])
            for t in self.obj.get_artist_top_tracks(self.ARTIST_ID)["items"]
        )

    def test_get_artist_videos(self):
        assert all(
            self.ARTIST_ID in (a["id"] for a in v["artists"])
            for v in self.obj.get_artist_videos(self.ARTIST_ID)["items"]
        )

    def test_get_artist_mix_id(self):
        mix_id = self.obj.get_artist_mix_id(self.ARTIST_ID)
        assert isinstance(mix_id, str) and len(mix_id) == 30

    def test_get_artist_radio(self):
        assert all(
            "trackNumber" in t
            for t in self.obj.get_artist_radio(self.ARTIST_ID)["items"]
        )

    def test_get_artist_biography(self):
        assert all(
            k in self.obj.get_artist_biography(self.ARTIST_ID)
            for k in {"source", "lastUpdated", "text", "summary"}
        )

    def test_get_artist_links(self):
        assert all(
            k in u
            for u in self.obj.get_artist_links(self.ARTIST_ID)["items"]
            for k in {"url", "siteName"}
        )

    def test_get_similar_artists(self):
        assert all(
            "artistRoles" in a
            for a in self.obj.get_similar_artists(self.ARTIST_ID)["items"]
        )

    def test_get_country_code(self):
        country_code = self.obj.get_country_code()
        assert isinstance(country_code, str) and len(country_code) == 2

    def test_get_mix_items(self):
        assert all(
            i["type"] == "track" for i in self.obj.get_mix_items(self.MIX_UUID)["items"]
        )

    def test_get_playlist(self):
        assert self.obj.get_playlist(self.PLAYLIST_UUID)["uuid"] == self.PLAYLIST_UUID

    def test_get_playlist_items(self):
        assert all(
            i["type"] == "track"
            for i in self.obj.get_playlist_items(self.PLAYLIST_UUID)["items"]
        )

    def test_search(self):
        assert self.obj.search("Beyoncé")["topHit"]["type"] == "ARTISTS"

    def test_get_track(self):
        assert self.obj.get_track(self.TRACK_ID)["id"] == self.TRACK_ID

    def test_get_track_contributors(self):
        assert all(
            k in c
            for c in self.obj.get_track_contributors(self.TRACK_ID)["items"]
            for k in {"name", "role"}
        )

    def test_get_track_credits(self):
        assert all(
            k in c
            for c in self.obj.get_track_credits(self.TRACK_ID)
            for k in {"type", "contributors"}
        )

    def test_get_track_composers(self):
        assert isinstance(self.obj.get_track_composers(self.TRACK_ID), list)

    def test_get_track_mix_id(self):
        mix_id = self.obj.get_track_mix_id(self.TRACK_ID)
        assert isinstance(mix_id, str) and len(mix_id) == 30

    def test_get_video(self):
        assert self.obj.get_video(self.VIDEO_ID)["id"] == self.VIDEO_ID


test = TestPrivateAPI()
test.setup_class()
test.test_get_similar_albums()

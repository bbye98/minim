from pathlib import Path
import sys

sys.path.insert(0, f"{Path(__file__).parents[1]}/src")
from minim import spotify  # noqa: E402

# class TestPrivateLyricsService:
#
#     TRACK_ID = "0VjIjW4GlUZAMYd2vXMi3b"
#
#     @classmethod
#     def setup_class(cls):
#         cls.obj = spotify.PrivateLyricsService()
#
#     def test_get_lyrics(self):
#         r = self.obj.get_lyrics(self.TRACK_ID)
#         assert "lyrics" in r


class TestWebAPI:

    ALBUM_IDS = [
        "382ObEPsp2rxGrnsizN5TX",
        "1A2GTWGtFfWp7KSQTwWOyo",
        "2noRn2Aes5aoNVsU6iWThc",
    ]
    ARTIST_IDS = [
        "2CIMQHirSU0MQqyYHq0eOx",
        "57dN52uHvrHOxijzpIgu3E",
        "1vCWHaC5f2uS3yhpwWbIA6",
    ]
    AUDIOBOOK_IDS = [
        "18yVqkdbdRvS24c0Ilj2ci",
        "1HGw3J3NxZO1TP1BTtVhpZ",
        "7iHfbu1YPACw6oZPAFJtqe",
    ]
    CHAPTER_IDS = [
        "0IsXVP0JmcB2adSE338GkK",
        "3ZXb8FKZGU0EHALYX6uCzU",
        "0D5wENdkdwbqlrHoaJ9g29",
    ]
    EPISODE_IDS = [
        "6UGk2IXiMig0yFewumiW7D",
        "4ffPDgch69iJi9lk2fNDmE",
        "2rRD6Erz15N54zqKr3AFS7",
    ]
    PLAYLIST_ID = "3cEYpjA9oz9GiPac4AsH4n"
    SHOW_IDS = [
        "03u3CF5jy51WnvG1ry77gA",
        "3L9tzrt0CthF6hNkxYIeSB",
        "5GmI4bfR8mP9815Y3oLGHc",
    ]
    TRACK_IDS = [
        "7ouMYWpwJ422jRcDASZB7P",
        "4VqPOruhp5EdPBeR92t6lQ",
        "2takcwOaAZWiXQijPHIx7B",
    ]

    @classmethod
    def setup_class(cls):
        cls.obj = spotify.WebAPI()

    def test_get_album(self):
        assert self.obj.get_album(self.ALBUM_IDS[0])["id"] == self.ALBUM_IDS[0]

    def test_get_albums(self):
        assert all(
            a["id"] == i
            for a, i in zip(self.obj.get_albums(self.ALBUM_IDS), self.ALBUM_IDS)
        )

    def test_get_album_tracks(self):
        assert self.ALBUM_IDS[0] in self.obj.get_album_tracks(self.ALBUM_IDS[0])["href"]

    def test_get_new_albums(self):
        assert all(a["type"] == "album" for a in self.obj.get_new_albums()["items"])

    def test_get_artist(self):
        assert self.obj.get_artist(self.ARTIST_IDS[0])["id"] == self.ARTIST_IDS[0]

    def test_get_artists(self):
        assert all(
            a["id"] == i
            for a, i in zip(self.obj.get_artists(self.ARTIST_IDS), self.ARTIST_IDS)
        )

    def test_get_artist_albums(self):
        assert (
            self.ARTIST_IDS[0] in self.obj.get_artist_albums(self.ARTIST_IDS[0])["href"]
        )

    def test_get_artist_top_tracks(self):
        assert all(
            self.ARTIST_IDS[0] in (a["id"] for a in t["artists"])
            for t in self.obj.get_artist_top_tracks(self.ARTIST_IDS[0])
        )

    def test_get_related_artists(self):
        assert all(
            a["type"] == "artist"
            for a in self.obj.get_related_artists(self.ARTIST_IDS[0])
        )

    def test_get_audiobook(self):
        assert (
            self.obj.get_audiobook(self.AUDIOBOOK_IDS[0])["id"] == self.AUDIOBOOK_IDS[0]
        )

    def test_get_audiobooks(self):
        assert all(
            a["id"] == i
            for a, i in zip(
                self.obj.get_audiobooks(self.AUDIOBOOK_IDS), self.AUDIOBOOK_IDS
            )
        )

    def test_get_audiobook_chapters(self):
        assert (
            self.AUDIOBOOK_IDS[0]
            in self.obj.get_audiobook_chapters(self.AUDIOBOOK_IDS[0])["href"]
        )

    def test_get_category(self):
        assert self.obj.get_category("dinner")["id"] == "0JQ5DAqbMKFRY5ok2pxXJ0"

    def test_get_categories(self):
        assert "browse/categories" in self.obj.get_categories()["href"]

    def test_get_chapter(self):
        assert (
            self.obj.get_chapter(self.CHAPTER_IDS[0], market="US")["id"]
            == self.CHAPTER_IDS[0]
        )

    def test_get_chapters(self):
        assert all(
            c["id"] == i
            for c, i in zip(
                self.obj.get_episodes(self.CHAPTER_IDS, market="US"), self.CHAPTER_IDS
            )
        )

    def test_get_episode(self):
        assert (
            self.obj.get_episode(self.EPISODE_IDS[0], market="US")["id"]
            == self.EPISODE_IDS[0]
        )

    def test_get_episodes(self):
        assert all(
            e["id"] == i
            for e, i in zip(
                self.obj.get_episodes(self.EPISODE_IDS, market="US"), self.EPISODE_IDS
            )
        )

    def test_get_genre_seeds(self):
        assert isinstance(self.obj.get_genre_seeds(), list)

    def test_get_markets(self):
        assert isinstance(self.obj.get_markets(), list)

    def test_get_playlist(self):
        assert self.obj.get_playlist(self.PLAYLIST_ID)["id"] == self.PLAYLIST_ID

    def test_get_playlist_cover_image(self):
        assert isinstance(self.obj.get_playlist_cover_image(self.PLAYLIST_ID), dict)

    def test_search(self):
        assert all(
            r["type"] == "album"
            for r in self.obj.search(
                "remaster%20track:Doxy%20artist:Miles%20Davis", "album"
            )["items"]
        )

    def test_get_show(self):
        assert (
            self.obj.get_show(self.SHOW_IDS[0], market="US")["id"] == self.SHOW_IDS[0]
        )

    def test_get_shows(self):
        assert all(
            s["type"] == "show" for s in self.obj.get_shows(self.SHOW_IDS, market="US")
        )

    def test_get_show_episodes(self):
        assert (
            self.SHOW_IDS[0]
            in self.obj.get_show_episodes(self.SHOW_IDS[0], market="US")["href"]
        )

    def test_get_track(self):
        assert self.obj.get_track(self.TRACK_IDS[0])["id"] == self.TRACK_IDS[0]

    def test_get_tracks(self):
        assert all(
            t["id"] == i
            for t, i in zip(self.obj.get_tracks(self.TRACK_IDS), self.TRACK_IDS)
        )

    def test_get_track_audio_features(self):
        features = self.obj.get_track_audio_features(self.TRACK_IDS[0])
        assert (
            features["id"] == self.TRACK_IDS[0] and features["type"] == "audio_features"
        )

    def test_get_tracks_audio_features(self):
        assert all(
            f["id"] == i and f["type"] == "audio_features"
            for f, i in zip(
                self.obj.get_tracks_audio_features(self.TRACK_IDS), self.TRACK_IDS
            )
        )

    def test_get_track_audio_analysis(self):
        assert "meta" in self.obj.get_track_audio_analysis(self.TRACK_IDS[0])

    def test_get_recommendations(self):
        recommendations = self.obj.get_recommendations(
            "4NHQUGzhtTLFvgF5SZesLK", "classical", "0c6xIDDpzE81m2q797ordA"
        )
        assert "seeds" in recommendations and "tracks" in recommendations

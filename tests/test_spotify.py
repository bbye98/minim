from pathlib import Path
import sys

sys.path.insert(0, f"{Path(__file__).parents[1]}/src")
from minim import spotify

class TestLyricsService:

    TRACK_ID = "1r0HKINDPff9jZQP9AzBr7"

    @classmethod
    def setup_class(cls):
        cls.session = spotify.LyricsService()

    def test_get_lyrics(self):
        resp = self.session.get_lyrics(self.TRACK_ID)
        assert "lyrics" in resp
 
class TestWebAPI:

    ALBUM_IDS = ["382ObEPsp2rxGrnsizN5TX", "1A2GTWGtFfWp7KSQTwWOyo", 
                 "2noRn2Aes5aoNVsU6iWThc"]
    ARTIST_IDS = ["2CIMQHirSU0MQqyYHq0eOx", "57dN52uHvrHOxijzpIgu3E", 
                  "1vCWHaC5f2uS3yhpwWbIA6"]
    AUDIOBOOK_IDS = ["18yVqkdbdRvS24c0Ilj2ci", "1HGw3J3NxZO1TP1BTtVhpZ",
                     "7iHfbu1YPACw6oZPAFJtqe"]
    CHAPTER_IDS = ["0IsXVP0JmcB2adSE338GkK", "3ZXb8FKZGU0EHALYX6uCzU",
                   "0D5wENdkdwbqlrHoaJ9g29"]
    # EPISODE_IDS = ["512ojhOuo1ktJprKbVcKyQ", "77o6BIVlYM3msb4MMIL1jH",
    #                "0Q86acNRm6V9GYx55SXKwf"]
    # SHOW_IDS = ["38bS44xjbVVZ3No3ByF1dJ", "5CfCWKI5pZ28U0uOzXkDHe", 
    #             "5as3aKmN2k11yfDDDSrvaZ"]
    TRACK_IDS = ["7ouMYWpwJ422jRcDASZB7P", "4VqPOruhp5EdPBeR92t6lQ",
                 "2takcwOaAZWiXQijPHIx7B"]

    @classmethod
    def setup_class(cls):
        Path(spotify.HOME_DIR / "minim.cfg").unlink(missing_ok=True)
        cls.session = spotify.WebAPI(flow="client_credentials")

    # def test_no_flow(self):
    #     Spotify = spotify.WebAPI()
    #     assert "Bearer" in Spotify.session.headers["Authorization"]

    # def test_authorization_code_flow(self):
    #     # Get access token using authorization code flow
    #     Spotify = spotify.WebAPI(flow="authorization_code", 
    #                              scopes=spotify.WebAPI.get_scopes("all"),
    #                              framework="flask")
    #     authorization = Spotify.session.headers["Authorization"]
    #     # Retrieve access token from configuration file
    #     Spotify = spotify.WebAPI()
    #     assert Spotify.session.headers["Authorization"] == authorization

    # def test_authorization_code_pkce_flow(self):
    #     # Get access token using authorization code with PKCE flow
    #     Spotify = spotify.WebAPI(flow="authorization_code_pkce", 
    #                              scopes=spotify.WebAPI.get_scopes("all"),
    #                              framework="flask")
    #     authorization = Spotify.session.headers["Authorization"]
    #     # Retrieve access token from configuration file
    #     Spotify = spotify.WebAPI()
    #     assert Spotify.session.headers["Authorization"] == authorization

    # def test_client_credentials_flow(self):
    #     # Get access token using client credentials flow
    #     Spotify = spotify.WebAPI(flow="client_credentials")
    #     authorization = Spotify.session.headers["Authorization"]
    #     # Retrieve access token from configuration file
    #     Spotify = spotify.WebAPI()
    #     assert Spotify.session.headers["Authorization"] == authorization

    def test_get_album(self):
        resp = self.session.get_album(self.ALBUM_IDS[0])
        assert resp["id"] == self.ALBUM_IDS[0]

    def test_get_albums(self):
        resp = self.session.get_albums(self.ALBUM_IDS)
        assert all(r["id"] == i for r, i in zip(resp, self.ALBUM_IDS))

    def test_get_album_tracks(self):
        resp = self.session.get_album_tracks(self.ALBUM_IDS[0])
        assert self.ALBUM_IDS[0] in resp["href"]

    def test_get_new_albums(self):
        resp = self.session.get_new_albums()
        assert all(r["type"] == "album" for r in resp["items"])

    def test_get_artist(self):
        resp = self.session.get_artist(self.ARTIST_IDS[0])
        assert resp["id"] == self.ARTIST_IDS[0]

    def test_get_artists(self):
        resp = self.session.get_artists(self.ARTIST_IDS)
        assert all(r["id"] == i for r, i in zip(resp, self.ARTIST_IDS))

    def test_get_artist_albums(self):
        resp = self.session.get_artist_albums(self.ARTIST_IDS[0])
        assert self.ARTIST_IDS[0] in resp["href"]

    def test_get_artist_top_tracks(self):
        resp = self.session.get_artist_top_tracks(self.ARTIST_IDS[0])
        assert all(self.ARTIST_IDS[0] in (a["id"] for a in r["artists"])
                   for r in resp)
        
    def test_get_related_artists(self):
        resp = self.session.get_related_artists(self.ARTIST_IDS[0])
        assert all(r["type"] == "artist" for r in resp)

    def test_get_audiobook(self):
        resp = self.session.get_audiobook(self.AUDIOBOOK_IDS[0])
        assert resp["id"] == self.AUDIOBOOK_IDS[0]

    def test_get_audiobooks(self):
        resp = self.session.get_audiobooks(self.AUDIOBOOK_IDS)
        assert all(r["id"] == i for r, i in zip(resp, self.AUDIOBOOK_IDS))

    def test_get_audiobook_chapters(self):
        resp = self.session.get_audiobook_chapters(self.AUDIOBOOK_IDS[0])
        assert self.AUDIOBOOK_IDS[0] in resp["href"]

    def test_get_category(self):
        resp = self.session.get_category("dinner")
        assert resp["id"] == "0JQ5DAqbMKFRY5ok2pxXJ0"

    def test_get_categories(self):
        resp = self.session.get_categories()
        assert "browse/categories" in resp["href"]

    def test_get_chapter(self):
        resp = self.session.get_chapter(self.CHAPTER_IDS[0], market="US")
        assert resp["id"] == self.CHAPTER_IDS[0]

    def test_get_chapters(self):
        resp = self.session.get_episodes(self.CHAPTER_IDS, market="US")
        assert all(r["id"] == i for r, i in zip(resp, self.CHAPTER_IDS))

    # def test_get_episode(self):
    #     resp = self.session.get_episode(self.EPISODE_IDS[0], market="US")
    #     assert resp["id"] == self.EPISODE_IDS[0]

    # def test_get_episodes(self):
    #     resp = self.session.get_episodes(self.EPISODE_IDS, market="US")
    #     assert all(r["id"] == i for r, i in zip(resp, self.EPISODE_IDS))

    def test_get_genre_seeds(self):
        resp = self.session.get_genre_seeds()
        assert isinstance(resp, list)

    def test_get_markets(self):
        resp = self.session.get_genre_seeds()
        assert isinstance(resp, list)

    def test_get_playlist(self):
        resp = self.session.get_playlist("3cEYpjA9oz9GiPac4AsH4n")
        assert resp["id"] == "3cEYpjA9oz9GiPac4AsH4n"

    def test_get_playlist_cover_image(self):
        resp = self.session.get_playlist_cover_image("3cEYpjA9oz9GiPac4AsH4n")
        assert isinstance(resp, dict)

    def test_search(self):
        resp = self.session.search(
            "remaster%20track:Doxy%20artist:Miles%20Davis", "album"
        )
        assert all(r["type"] == "album" for r in resp["items"])

    # def test_get_show(self):
    #     resp = self.session.get_show(self.SHOW_IDS[0], market="US")
    #     assert resp["id"] == self.SHOW_IDS[0]

    # def test_get_shows(self):
    #     resp = self.session.get_shows(self.SHOW_IDS, market="US")
    #     assert all(r["type"] == "show" for r in resp)

    # def test_get_show_episodes(self):
    #     resp = self.session.get_show_episodes(self.SHOW_IDS[0], market="US")
    #     assert self.SHOW_IDS[0] in resp["href"]

    def test_get_track(self):
        resp = self.session.get_track(self.TRACK_IDS[0])
        assert resp["id"] == self.TRACK_IDS[0]

    def test_get_tracks(self):
        resp = self.session.get_tracks(self.TRACK_IDS)
        assert all(r["id"] == i for r, i in zip(resp, self.TRACK_IDS))

    def test_get_track_audio_features(self):
        resp = self.session.get_track_audio_features(self.TRACK_IDS[0])
        assert resp["id"] == self.TRACK_IDS[0] \
               and resp["type"] == "audio_features"
        
    def test_get_tracks_audio_features(self):
        resp = self.session.get_tracks_audio_features(self.TRACK_IDS)
        assert all(r["id"] == i and r["type"] == "audio_features" 
                   for r, i in zip(resp, self.TRACK_IDS))
        
    def test_get_track_audio_analysis(self):
        resp = self.session.get_track_audio_analysis(self.TRACK_IDS[0])
        assert "meta" in resp

    def test_get_recommendations(self):
        resp = self.session.get_recommendations("4NHQUGzhtTLFvgF5SZesLK",
                                                "classical", 
                                                "0c6xIDDpzE81m2q797ordA")
        assert "seeds" in resp and "tracks" in resp
from pathlib import Path
import sys

sys.path.insert(0, f"{Path(__file__).parents[1]}/src")
from minim import discogs  # noqa: E402


class TestAPI:

    ARTIST_ID = 108713
    LABEL_ID = 1
    MASTER_RELEASE_ID = 1000
    RELEASE_ID = 249504
    USERNAME = "bbye98"

    @classmethod
    def setup_class(cls):
        cls.obj = discogs.API(flow="discogs")

    def test_get_release(self):
        assert self.obj.get_release(self.RELEASE_ID)["id"] == self.RELEASE_ID

    def test_get_user_release_rating(self):
        assert (
            self.obj.get_user_release_rating(self.RELEASE_ID, self.USERNAME)[
                "release_id"
            ]
            == self.RELEASE_ID
        )

    def test_get_community_release_rating(self):
        assert (
            self.obj.get_community_release_rating(self.RELEASE_ID)["release_id"]
            == self.RELEASE_ID
        )

    # def test_get_release_stats(self):
    #     r = self.obj.get_release_stats(self.RELEASE_ID)
    #     assert "num_have" in r and "num_want" in r

    def test_get_master_release(self):
        assert (
            self.obj.get_master_release(self.MASTER_RELEASE_ID)["id"]
            == self.MASTER_RELEASE_ID
        )

    def test_get_master_release_versions(self):
        assert "versions" in self.obj.get_master_release_versions(
            self.MASTER_RELEASE_ID
        )

    def test_get_artist(self):
        assert self.obj.get_artist(self.ARTIST_ID)["id"] == self.ARTIST_ID

    def test_get_artist_releases(self):
        assert "releases" in self.obj.get_artist_releases(self.ARTIST_ID)

    def test_get_label(self):
        assert self.obj.get_label(self.LABEL_ID)["id"] == self.LABEL_ID

    def test_get_label_releases(self):
        assert "releases" in self.obj.get_label_releases(self.LABEL_ID)

    def test_search(self):
        assert "results" in self.obj.search(title="Nirvana - Nevermind")

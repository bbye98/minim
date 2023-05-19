import pathlib
import sys

sys.path.insert(0, f"{pathlib.Path(__file__).parents[1].resolve()}/src")
from minim import itunes

class TestiTunes:

    def test_search(self):
        term = "Jack Johnson"
        assert any(any(term in v for v in r.values() if isinstance(v, str))
                for r in itunes.search(term)["results"])

    def test_search_limit(self):
        limit = 25
        assert itunes.search("Jack Johnson", limit=limit)["resultCount"] <= limit

    def test_search_entity(self):
        assert all(r["kind"] == "music-video"
                for r in itunes.search("Jack Johnson",
                                        entity="musicVideo")["results"])

    def test_search_country(self):
        assert all(r["country"] == "CAN"
                for r in itunes.search("Jim Jones", country="CA")["results"])

    def test_search_country_entity(self):
        assert all(r["kind"] == "software" and r["currency"] == "USD"
                for r in itunes.search("Yelp", country="US",
                                        entity="software")["results"])

    def test_lookup_artist(self):
        assert itunes.lookup(909253)["results"][0]["artistName"] == "Jack Johnson"
        assert itunes.lookup("909253")["results"][0]["artistName"] == "Jack Johnson"

    def test_lookup_app(self):
        assert "Yelp" in itunes.lookup(284910350)["results"][0]["trackName"]

    def test_lookup_amg_artist(self):
        assert itunes.lookup(amg_artist_id=468749)["results"][0]["artistName"] \
            == "Jack Johnson"
        assert itunes.lookup(amg_artist_id="468749")["results"][0]["artistName"] \
            == "Jack Johnson"

    def test_lookup_artists(self):
        assert itunes.lookup(amg_artist_id=[468749, 5723])["resultCount"] == 2
        assert itunes.lookup(amg_artist_id="468749,5723")["resultCount"] == 2

    def test_lookup_artist_entity(self):
        resp = itunes.lookup(909253, entity="album")
        assert any("Jack Johnson" in r["artistName"] for r in resp["results"]) \
            and resp["results"][0]["wrapperType"] == "artist" \
            and all(r["collectionType"] == "Album" for r in resp["results"][1:])

    def test_lookup_amg_artists_entity_limit_sort(self):
        resp = itunes.lookup(amg_artist_id="468749,5723", entity="album", limit=5, sort="recent")
        assert resp["results"][0]["wrapperType"] == "artist" \
            and resp["results"][6]["wrapperType"] == "artist" \
            and all(i["collectionType"] == "Album" for i in resp["results"][1:6]) \
            and all(i["collectionType"] == "Album" for i in resp["results"][7:]) \
            and resp["resultCount"] == 12

    def test_lookup_upc(self):
        assert itunes.lookup(upc=720642462928)["results"][0]["collectionName"] \
            == "Weezer"
        assert itunes.lookup(upc="720642462928")["results"][0]["collectionName"] \
            == "Weezer"

    def test_lookup_upc_entity(self):
        assert all(r["artistName"] == "Weezer"
                for r in itunes.lookup(upc=720642462928, entity="song")["results"])

    def test_lookup_isbn(self):
        assert itunes.lookup(isbn=9780316069359)["results"][0]["trackName"] \
            == "The Fifth Witness"
        assert itunes.lookup(isbn="9780316069359")["results"][0]["trackName"] \
            == "The Fifth Witness"

    def test_lookup_bundle(self):
        assert "Yelp" in itunes.lookup(bundle_id="com.yelp.yelpiphone")["results"][0]["trackName"]
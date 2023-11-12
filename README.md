<picture>
  <source media="(prefers-color-scheme: dark)" 
   srcset="https://raw.githubusercontent.com/bbye98/minim/main/assets/logo_dark.svg">
  <source media="(prefers-color-scheme: light)" 
   srcset="https://raw.githubusercontent.com/bbye98/minim/main/assets/logo_light.svg">
  <img alt="minim logo" 
   src="https://raw.githubusercontent.com/bbye98/minim/main/assets/logo_light.svg">
</picture>
<br></br>

# Minim

[![continuous-integration](https://github.com/bbye98/minim/actions/workflows/ci.yml/badge.svg)](https://github.com/bbye98/minim/actions/workflows/ci.yml)

Minim is a lightweight Python 3 library that can interface with APIs 
by popular music services—iTunes, Qobuz, Spotify, and TIDAL—and operate 
on audio files, such as updating metadata and converting between audio
formats.

* **Documentation**: https://bbye98.github.io/minim/

## Features

* [`minim.audio`](https://github.com/bbye98/minim/blob/main/src/minim/audio.py):
  Audio file handlers for reading and writing metadata and converting
  between audio formats.
* [`minim.itunes`](https://github.com/bbye98/minim/blob/main/src/minim/itunes.py):
  A client for the iTunes Search API.
* [`minim.qobuz`](https://github.com/bbye98/minim/blob/main/src/minim/qobuz.py):
  A client for the Qobuz API with support for the password grant type 
  for user authentication and user authentication token caching.
* [`minim.spotify`](https://github.com/bbye98/minim/blob/main/src/minim/spotify.py):
  Clients for the Spotify Lyrics service and the Spotify Web API with
  support for the authorization code, authorization code with proof key
  for code exchange (PKCE), and client credentials grant types, and
  access token caching.
* [`minim.tidal`](https://github.com/bbye98/minim/blob/main/src/minim/tidal.py):
  Clients for the old and new TIDAL APIs with support for the 
  authorization code with PKCE and client credentials grant types, and
  access token caching.

## Installation

Minim requires Python 3.9 or later.

Clone the repository and install the package using pip:

    git clone https://github.com/bbye98/minim.git
    cd minim
    python -m pip install -e .

## Examples

- Import Minim and create clients for the different APIs. Additional 
  keyword arguments can be passed to the constructors to control user
  authentication.

      >>> from minim import itunes, qobuz, spotify, tidal
      >>> client_itunes = itunes.SearchAPI()
      >>> client_qobuz = qobuz.PrivateAPI()
      >>> client_spotify = spotify.WebAPI(flow="web_player")
      >>> client_tidal = tidal.PrivateAPI(client_id=<TIDAL_CLIENT_ID>)

- Search for and retrieve information about an artist, such as the EDM 
  group Galantis:

  **iTunes Search API**

      >>> client_itunes.search("Galantis", entity="musicArtist", 
      ...                      limit=1)["results"][0]

  <details>
  <summary>Output</summary>

      {
        "wrapperType": "artist",
        "artistType": "Artist",
        "artistName": "Galantis",
        "artistLinkUrl": "https://music.apple.com/us/artist/galantis/543322169?uo=4",
        "artistId": 543322169,
        "amgArtistId": 2616267,
        "primaryGenreName": "Dance",
        "primaryGenreId": 17
      }

  </details>

  **Private Qobuz API**

      >>> client_qobuz.search("Galantis", limit=1, 
      ...                     strict=True)["artists"]["items"][0]

  <details>
  <summary>Output</summary>

      {
        "picture": "https://static.qobuz.com/images/artists/covers/small/8dcf30e5c8e30281ecbb13b0886426c8.jpg",
        "image": {
          "small": "https://static.qobuz.com/images/artists/covers/small/8dcf30e5c8e30281ecbb13b0886426c8.jpg",
          "medium": "https://static.qobuz.com/images/artists/covers/medium/8dcf30e5c8e30281ecbb13b0886426c8.jpg",
          "large": "https://static.qobuz.com/images/artists/covers/large/8dcf30e5c8e30281ecbb13b0886426c8.jpg",
          "extralarge": "https://static.qobuz.com/images/artists/covers/large/8dcf30e5c8e30281ecbb13b0886426c8.jpg",
          "mega": "https://static.qobuz.com/images/artists/covers/large/8dcf30e5c8e30281ecbb13b0886426c8.jpg"
        },
        "name": "Galantis",
        "slug": "galantis",
        "albums_count": 126,
        "id": 865362
      }
  
  </details>

  **Spotify Web API**

      >>> client_spotify.search("Galantis", "artist", limit=1)["items"][0]

  <details>
  <summary>Output</summary>

      {
        "external_urls": {
          "spotify": "https://open.spotify.com/artist/4sTQVOfp9vEMCemLw50sbu"
        },
        "followers": {
          "href": null,
          "total": 3373205
        },
        "genres": [
          "dance pop",
          "edm",
          "pop",
          "pop dance"
        ],
        "href": "https://api.spotify.com/v1/artists/4sTQVOfp9vEMCemLw50sbu",
        "id": "4sTQVOfp9vEMCemLw50sbu",
        "images": [
          {
            "height": 640,
            "url": "https://i.scdn.co/image/ab6761610000e5eb7bda087d6fb48d481efd3344",
            "width": 640
          },
          {
            "height": 320,
            "url": "https://i.scdn.co/image/ab676161000051747bda087d6fb48d481efd3344",
            "width": 320
          },
          {
            "height": 160,
            "url": "https://i.scdn.co/image/ab6761610000f1787bda087d6fb48d481efd3344",
            "width": 160
          }
        ],
        "name": "Galantis",
        "popularity": 67,
        "type": "artist",
        "uri": "spotify:artist:4sTQVOfp9vEMCemLw50sbu"
      }
  
  </details>

  **Private TIDAL API**
    
      >>> client_tidal.search("Galantis", type="artist", limit=1)["items"][0]

  <details>
  <summary>Output</summary>

      {
        "id": 4676988,
        "name": "Galantis",
        "artistTypes": [
          "ARTIST",
          "CONTRIBUTOR"
        ],
        "url": "http://www.tidal.com/artist/4676988",
        "picture": "a627e21c-60f7-4e90-b2bb-e50b178c4f0b",
        "popularity": 72,
        "artistRoles": [
          {
            "categoryId": -1,
            "category": "Artist"
          },
          {
            "categoryId": 11,
            "category": "Performer"
          },
          {
            "categoryId": 3,
            "category": "Engineer"
          },
          {
            "categoryId": 10,
            "category": "Production team"
          },
          {
            "categoryId": 1,
            "category": "Producer"
          },
          {
            "categoryId": 2,
            "category": "Songwriter"
          }
        ],
        "mixes": {
          "ARTIST_MIX": "000202a7e72fd90d0c0df2ed56ddea"
        }
      }
  
  </details>

- Search for and retrieve information about a track, such as "Everybody Talks" by Neon Trees:

  **iTunes Search API**

      >>> client_itunes.search("Everybody Talks", media="music", 
      ...                      limit=1)["results"][0]

  <details>
  <summary>Output</summary>

      {
        "wrapperType": "track",
        "kind": "song",
        "artistId": 350172836,
        "collectionId": 1443469527,
        "trackId": 1443469581,
        "artistName": "Neon Trees",
        "collectionName": "Picture Show",
        "trackName": "Everybody Talks",
        "collectionCensoredName": "Picture Show",
        "trackCensoredName": "Everybody Talks",
        "artistViewUrl": "https://music.apple.com/us/artist/neon-trees/350172836?uo=4",
        "collectionViewUrl": "https://music.apple.com/us/album/everybody-talks/1443469527?i=1443469581&uo=4",
        "trackViewUrl": "https://music.apple.com/us/album/everybody-talks/1443469527?i=1443469581&uo=4",
        "previewUrl": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview122/v4/5c/29/bf/5c29bf6b-ca2c-4e8b-2be6-c51a282c7dae/mzaf_1255557534804450018.plus.aac.p.m4a",
        "artworkUrl30": "https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/80/e3/95/80e39565-35f9-2496-c6f8-6572490c4a7b/12UMGIM12509.rgb.jpg/30x30bb.jpg",
        "artworkUrl60": "https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/80/e3/95/80e39565-35f9-2496-c6f8-6572490c4a7b/12UMGIM12509.rgb.jpg/60x60bb.jpg",
        "artworkUrl100": "https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/80/e3/95/80e39565-35f9-2496-c6f8-6572490c4a7b/12UMGIM12509.rgb.jpg/100x100bb.jpg",
        "collectionPrice": 6.99,
        "trackPrice": 1.29,
        "releaseDate": "2011-12-19T12:00:00Z",
        "collectionExplicitness": "explicit",
        "trackExplicitness": "explicit",
        "discCount": 1,
        "discNumber": 1,
        "trackCount": 12,
        "trackNumber": 3,
        "trackTimeMillis": 177280,
        "country": "USA",
        "currency": "USD",
        "primaryGenreName": "Alternative",
        "contentAdvisoryRating": "Explicit",
        "isStreamable": true
      }

  </details>

  **Private Qobuz API**

      >>> client_qobuz.search("Everybody Talks", "ReleaseName", limit=1, 
      ...                     strict=True)["tracks"]["items"][0]

  <details>
  <summary>Output</summary>

      {
        "maximum_bit_depth": 16,
        "copyright": "\u2117 2011 UMG Recordings, Inc.",
        "performers": "Justin Meldal-Johnsen, Producer, Guitar, Additional Keyboards, Percussion, Programmer, AssociatedPerformer - Tim Pagnotta, ComposerLyricist - Greg Collins, Engineer, StudioPersonnel - Wesley Seidman, Asst. Recording Engineer, StudioPersonnel - Tyler Glenn, ComposerLyricist - Neon Trees, MainArtist - Matt Wiggers, Asst. Recording Engineer, StudioPersonnel - Bill Bush, Mixer, StudioPersonnel",
        "audio_info": {
          "replaygain_track_peak": 0.999969,
          "replaygain_track_gain": -11.63
        },
        "performer": {
          "name": "Neon Trees",
          "id": 470727
        },
        "album": {
          "image": {
            "small": "https://static.qobuz.com/images/covers/42/54/0060252795442_230.jpg",
            "thumbnail": "https://static.qobuz.com/images/covers/42/54/0060252795442_50.jpg",
            "large": "https://static.qobuz.com/images/covers/42/54/0060252795442_600.jpg"
          },
          "maximum_bit_depth": 16,
          "media_count": 1,
          "artist": {
            "image": null,
            "name": "Neon Trees",
            "id": 470727,
            "albums_count": 42,
            "slug": "neon-trees",
            "picture": null
          },
          "upc": "0060252795442",
          "released_at": 1325372400,
          "label": {
            "name": "Mercury Records",
            "id": 17487,
            "albums_count": 774,
            "supplier_id": 1,
            "slug": "mercury-records"
          },
          "title": "Picture Show",
          "qobuz_id": 5653617,
          "version": null,
          "duration": 2785,
          "parental_warning": true,
          "tracks_count": 11,
          "popularity": 0,
          "genre": {
            "path": [112, 119, 113],
            "color": "#0070ef",
            "name": "Alternative & Indie",
            "id": 113,
            "slug": "alternatif-et-inde"
          },
          "maximum_channel_count": 2,
          "id": "0060252795442",
          "maximum_sampling_rate": 44.1,
          "previewable": true,
          "sampleable": true,
          "displayable": true,
          "streamable": true,
          "streamable_at": 1683529200,
          "downloadable": false,
          "purchasable_at": null,
          "purchasable": false,
          "release_date_original": "2012-01-01",
          "release_date_download": "2012-01-01",
          "release_date_stream": "2012-01-01",
          "release_date_purchase": "2012-01-01",
          "hires": false,
          "hires_streamable": false
        },
        "work": null,
        "composer": {
          "name": "Tyler Glenn",
          "id": 583118
        },
        "isrc": "USUM71119189",
        "title": "Everybody Talks",
        "version": "Album Version",
        "duration": 177,
        "parental_warning": true,
        "track_number": 3,
        "maximum_channel_count": 2,
        "id": 5653620,
        "media_number": 1,
        "maximum_sampling_rate": 44.1,
        "release_date_original": null,
        "release_date_download": null,
        "release_date_stream": null,
        "release_date_purchase": null,
        "purchasable": true,
        "streamable": true,
        "previewable": true,
        "sampleable": true,
        "downloadable": true,
        "displayable": true,
        "purchasable_at": 1683702000,
        "streamable_at": 1683529200,
        "hires": false,
        "hires_streamable": false
      }
  
  </details>

  **Spotify Web API**

      >>> client_spotify.search("Everybody Talks", "track", limit=1)["items"][0]

  <details>
  <summary>Output</summary>

      {
        "album": {
          "album_type": "album",
          "artists": [
            {
              "external_urls": {
                "spotify": "https://open.spotify.com/artist/0RpddSzUHfncUWNJXKOsjy"
              },
              "href": "https://api.spotify.com/v1/artists/0RpddSzUHfncUWNJXKOsjy",
              "id": "0RpddSzUHfncUWNJXKOsjy",
              "name": "Neon Trees",
              "type": "artist",
              "uri": "spotify:artist:0RpddSzUHfncUWNJXKOsjy"
            }
          ],
          "available_markets": [
            "AR", "AU", "AT", "BE", "BO", "BR", "BG", 
            "CA", "CL", "CO", "CR", "CY", "CZ", "DK",
            "DO", "DE", "EC", "EE", "SV", "FI", "FR", 
            "GR", "GT", "HN", "HK", "HU", "IS", "IE", 
            "IT", "LV", "LT", "LU", "MY", "MT", "NL", 
            "NZ", "NI", "NO", "PA", "PY", "PE", "PH", 
            "PL", "PT", "SG", "SK", "ES", "SE", "CH", 
            "TW", "TR", "UY", "US", "GB", "AD", "LI", 
            "MC", "ID", "TH", "VN", "RO", "IL", "ZA", 
            "SA", "AE", "BH", "QA", "OM", "KW", "EG", 
            "TN", "LB", "JO", "PS", "IN", "BY", "KZ", 
            "MD", "UA", "AL", "BA", "HR", "ME", "MK", 
            "RS", "SI", "KR", "BD", "PK", "LK", "GH",
            "KE", "NG", "TZ", "UG", "AG", "AM", "BS", 
            "BB", "BZ", "BT", "BW", "BF", "CV", "CW", 
            "DM", "FJ", "GM", "GD", "GW", "GY", "HT", 
            "JM", "KI", "LS", "LR", "MW", "MV", "ML", 
            "MH", "FM", "NA", "NR", "NE", "PW", "PG", 
            "WS", "ST", "SN", "SC", "SL", "SB", "KN", 
            "LC", "VC", "SR", "TL", "TO", "TT", "TV", 
            "AZ", "BN", "BI", "KH", "CM", "TD", "KM", 
            "GQ", "SZ", "GA", "GN", "KG", "LA", "MO", 
            "MR", "MN", "NP", "RW", "TG", "UZ", "ZW", 
            "BJ", "MG", "MU", "MZ", "AO", "CI", "DJ", 
            "ZM", "CD", "CG", "IQ", "TJ", "VE", "XK"
          ],
          "external_urls": {
            "spotify": "https://open.spotify.com/album/0uRFz92JmjwDbZbB7hEBIr"
          },
          "href": "https://api.spotify.com/v1/albums/0uRFz92JmjwDbZbB7hEBIr",
          "id": "0uRFz92JmjwDbZbB7hEBIr",
          "images": [
            {
              "height": 640,
              "url": "https://i.scdn.co/image/ab67616d0000b2734a6c0376235e5aa44e59d2c2",
              "width": 640
            },
            {
              "height": 300,
              "url": "https://i.scdn.co/image/ab67616d00001e024a6c0376235e5aa44e59d2c2",
              "width": 300
            },
            {
              "height": 64,
              "url": "https://i.scdn.co/image/ab67616d000048514a6c0376235e5aa44e59d2c2",
              "width": 64
            }
          ],
          "name": "Picture Show",
          "release_date": "2012-01-01",
          "release_date_precision": "day",
          "total_tracks": 11,
          "type": "album",
          "uri": "spotify:album:0uRFz92JmjwDbZbB7hEBIr"
        },
        "artists": [
          {
            "external_urls": {
              "spotify": "https://open.spotify.com/artist/0RpddSzUHfncUWNJXKOsjy"
            },
            "href": "https://api.spotify.com/v1/artists/0RpddSzUHfncUWNJXKOsjy",
            "id": "0RpddSzUHfncUWNJXKOsjy",
            "name": "Neon Trees",
            "type": "artist",
            "uri": "spotify:artist:0RpddSzUHfncUWNJXKOsjy"
          }
        ],
        "available_markets": [
          "AR", "AU", "AT", "BE", "BO", "BR", "BG", 
          "CA", "CL", "CO", "CR", "CY", "CZ", "DK",
          "DO", "DE", "EC", "EE", "SV", "FI", "FR", 
          "GR", "GT", "HN", "HK", "HU", "IS", "IE", 
          "IT", "LV", "LT", "LU", "MY", "MT", "NL", 
          "NZ", "NI", "NO", "PA", "PY", "PE", "PH", 
          "PL", "PT", "SG", "SK", "ES", "SE", "CH", 
          "TW", "TR", "UY", "US", "GB", "AD", "LI", 
          "MC", "ID", "TH", "VN", "RO", "IL", "ZA", 
          "SA", "AE", "BH", "QA", "OM", "KW", "EG", 
          "TN", "LB", "JO", "PS", "IN", "BY", "KZ", 
          "MD", "UA", "AL", "BA", "HR", "ME", "MK", 
          "RS", "SI", "KR", "BD", "PK", "LK", "GH",
          "KE", "NG", "TZ", "UG", "AG", "AM", "BS", 
          "BB", "BZ", "BT", "BW", "BF", "CV", "CW", 
          "DM", "FJ", "GM", "GD", "GW", "GY", "HT", 
          "JM", "KI", "LS", "LR", "MW", "MV", "ML", 
          "MH", "FM", "NA", "NR", "NE", "PW", "PG", 
          "WS", "ST", "SN", "SC", "SL", "SB", "KN", 
          "LC", "VC", "SR", "TL", "TO", "TT", "TV", 
          "AZ", "BN", "BI", "KH", "CM", "TD", "KM", 
          "GQ", "SZ", "GA", "GN", "KG", "LA", "MO", 
          "MR", "MN", "NP", "RW", "TG", "UZ", "ZW", 
          "BJ", "MG", "MU", "MZ", "AO", "CI", "DJ", 
          "ZM", "CD", "CG", "IQ", "TJ", "VE", "XK"
        ],
        "disc_number": 1,
        "duration_ms": 177280,
        "explicit": true,
        "external_ids": {
          "isrc": "USUM71119189"
        },
        "external_urls": {
          "spotify": "https://open.spotify.com/track/2iUmqdfGZcHIhS3b9E9EWq"
        },
        "href": "https://api.spotify.com/v1/tracks/2iUmqdfGZcHIhS3b9E9EWq",
        "id": "2iUmqdfGZcHIhS3b9E9EWq",
        "is_local": false,
        "name": "Everybody Talks",
        "popularity": 81,
        "preview_url": null,
        "track_number": 3,
        "type": "track",
        "uri": "spotify:track:2iUmqdfGZcHIhS3b9E9EWq"
      }
  
  </details>

  **Private TIDAL API**
    
      >>> client_tidal.search("Everybody Talks", type="track", 
      ...                     limit=1)["items"][0]

  <details>
  <summary>Output</summary>

      {
        "id": 14492425,
        "title": "Everybody Talks",
        "duration": 177,
        "replayGain": -11.7,
        "peak": 0.999969,
        "allowStreaming": true,
        "streamReady": true,
        "adSupportedStreamReady": true,
        "djReady": true,
        "stemReady": false,
        "streamStartDate": "2012-04-17T00:00:00.000+0000",
        "premiumStreamingOnly": false,
        "trackNumber": 3,
        "volumeNumber": 1,
        "version": null,
        "popularity": 55,
        "copyright": "A Mercury Records Release; \u2117 2011 UMG Recordings, Inc.",
        "url": "http://www.tidal.com/track/14492425",
        "isrc": "USUM71119189",
        "editable": false,
        "explicit": true,
        "audioQuality": "LOSSLESS",
        "audioModes": [
          "STEREO"
        ],
        "mediaMetadata": {
          "tags": [
            "LOSSLESS"
          ]
        },
        "artist": {
          "id": 3665225,
          "name": "Neon Trees",
          "type": "MAIN",
          "picture": "e6f17398-759e-45a0-9673-6ded6811e199"
        },
        "artists": [
          {
            "id": 3665225,
            "name": "Neon Trees",
            "type": "MAIN",
            "picture": "e6f17398-759e-45a0-9673-6ded6811e199"
          }
        ],
        "album": {
          "id": 14492422,
          "title": "Picture Show",
          "cover": "1c2d7c90-034e-485a-be1f-24a669c7e6ee",
          "vibrantColor": "#f8af88",
          "videoCover": null
        },
        "mixes": {
          "TRACK_MIX": "0019768c833a193c29829e5bf473fc"
        }
      }
  
  </details>

- If the clients are authenticated, you can create a user playlist and
  add tracks to it. Using the track IDs for "Everybody Talks" by Neon
  Trees from the previous example:

  **Private Qobuz API**

      >>> playlist_qobuz = client_qobuz.create_playlist(
      ...     "Minim", 
      ...     description="A playlist created using Minim."
      ... )
      >>> client_qobuz.add_playlist_tracks(playlist_qobuz["id"], 5653620)

  **Spotify Web API**

      >>> playlist_spotify = client_spotify.create_playlist(
      ...     "Minim", 
      ...     description="A playlist created using Minim."
      ... )
      >>> client_spotify.add_playlist_items(
      ...     playlist_spotify["id"], 
      ...     ["spotify:track:2iUmqdfGZcHIhS3b9E9EWq"]
      ... )

  **Private TIDAL API**

      >>> playlist_tidal = client_tidal.create_playlist(
      ...     "Minim", 
      ...     description="A playlist created using Minim."
      ... )
      >>> client_tidal.add_playlist_items(playlist_tidal["data"]["uuid"], 
      ...                                 14492425)
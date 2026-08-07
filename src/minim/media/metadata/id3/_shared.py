from __future__ import annotations

GENRES = {
    0: "Blues",
    1: "Classic Rock",
    2: "Country",
    3: "Dance",
    4: "Disco",
    5: "Funk",
    6: "Grunge",
    7: "Hip-Hop/Rap",
    8: "Jazz",
    9: "Metal",
    10: "New Age",
    11: "Oldies",
    12: "Other",
    13: "Pop",
    14: "R&B/Soul",
    15: "Rap",
    16: "Reggae",
    17: "Rock",
    18: "Techno",
    19: "Industrial",
    20: "Alternative",
    21: "Ska",
    22: "Death Metal",
    23: "Pranks",
    24: "Soundtrack",
    25: "Euro-Techno",
    26: "Ambient",
    27: "Trip-Hop",
    28: "Vocal",
    29: "Jazz/Funk",
    30: "Fusion",
    31: "Trance",
    32: "Classical",
    33: "Instrumental",
    34: "Acid",
    35: "House",
    36: "Game",
    37: "Sound Clip",
    38: "Gospel",
    39: "Noise",
    40: "Alternative Rock",
    41: "Bass",
    42: "Soul",
    43: "Punk",
    44: "Space",
    45: "Meditative",
    46: "Instrumental Pop",
    47: "Instrumental Rock",
    48: "Ethnic",
    49: "Gothic",
    50: "Darkwave",
    51: "Techno-Industrial",
    52: "Electronic",
    53: "Pop/Folk",
    54: "Eurodance",
    55: "Dream",
    56: "Southern Rock",
    57: "Comedy",
    58: "Cult",
    59: "Gangsta",
    60: "Top 40",
    61: "Christian Rap",
    62: "Pop/Funk",
    63: "Jungle",
    64: "Native American",
    65: "Cabaret",
    66: "New Wave",
    67: "Psychedelic",
    68: "Rave",
    69: "Showtunes",
    70: "Trailer",
    71: "Lo-Fi",
    72: "Tribal",
    73: "Acid Punk",
    74: "Acid Jazz",
    75: "Polka",
    76: "Retro",
    77: "Musical",
    78: "Rock & Roll",
    79: "Hard Rock",
    80: "Folk",
    81: "Folk-Rock",
    82: "National Folk",
    83: "Swing",
    84: "Fusion",
    85: "Bebop",
    86: "Latin",
    87: "Revival",
    88: "Celtic",
    89: "Bluegrass",
    90: "Avant-Garde",
    91: "Gothic Rock",
    92: "Progressive Rock",
    93: "Psychedelic Rock",
    94: "Symphonic Rock",
    95: "Soft Rock",
    96: "Big Band",
    97: "Chorus",
    98: "Easy Listening",
    99: "Acoustic",
    100: "Humor",
    101: "Speech",
    102: "Chanson",
    103: "Opera",
    104: "Chamber Music",
    105: "Sonata",
    106: "Symphony",
    107: "Booty Bass",
    108: "Primus",
    109: "Porn Groove",
    110: "Satire",
    111: "Slow Jam",
    112: "Club",
    113: "Tango",
    114: "Samba",
    115: "Folklore",
    116: "Ballad",
    117: "Power Ballad",
    118: "Rhythmic Soul",
    119: "Freestyle",
    120: "Duet",
    121: "Punk Rock",
    122: "Drum Solo",
    123: "A Cappella",
    124: "Euro-House",
    125: "Dancehall",
    126: "Goa",
    127: "Drum & Bass",
    128: "Club-House",
    129: "Hardcore",
    130: "Terror",
    131: "Indie",
    132: "Britpop",
    133: "Negerpunk",
    134: "Polish Punk",
    135: "Beat",
    136: "Christian Gangsta Rap",
    137: "Heavy Metal",
    138: "Black Metal",
    139: "Crossover",
    140: "Christian & Gospel",
    141: "Christian Rock",
    142: "Merengue",
    143: "Salsa",
    144: "Thrash Metal",
    145: "Anime",
    146: "J-Pop",
    147: "Synthpop",
    148: "Christmas",
    149: "Art Rock",
    150: "Baroque",
    151: "Bhangra",
    152: "Big Beat",
    153: "Breakbeat",
    154: "Chill-Out",
    155: "Downtempo",
    156: "Dub",
    157: "EBM",
    158: "Eclectic",
    159: "Electro",
    160: "Electro-Clash",
    161: "Emo",
    162: "Experimental",
    163: "Garage",
    164: "World",
    165: "IDM",
    166: "Illbient",
    167: "Industrial Goth",
    168: "Jam Bands",
    169: "Krautrock",
    170: "Leftfield",
    171: "Lounge",
    172: "Math Rock",
    173: "New Romantic",
    174: "Nu-Breaks",
    175: "Post-Punk",
    176: "Post-Rock",
    177: "Psy-Trance",
    178: "Shoegaze",
    179: "Space Rock",
    180: "Trop Rock",
    181: "World",
    182: "Neoclassical",
    183: "Audiobook",
    184: "Audio Theatre",
    185: "Neue Deutsche Welle",
    186: "Podcast",
    187: "Indie Rock",
    188: "G-Funk",
    189: "Dubstep",
    190: "Garage Rock",
    191: "Psybient",
}
GENRES |= {v.lower(): k for k, v in GENRES.items()}
TAG_VERSIONS = {(2, 2, 0), (2, 3, 0), (2, 4, 0)}


def normalize_id3v1_tag_version(
    tag_version: str | tuple[int, int], /
) -> tuple[int, int]:
    """
    Normalize ID3v1 tag version.

    Parameters
    ----------
    tag_version : str or tuple[int, int]; default: :code:`(1, 1)`
        ID3v1 tag version.

        **Valid values**: :code:`"1.0"` or :code:`(1, 0)`,
        :code:`"1.1"` or :code:`(1, 1)`.

    Returns
    -------
    tag_version : tuple[int, int]
        ID3v1 tag version.
    """
    match tag_version:
        case tuple() | list():
            return tag_version
        case str():
            return tuple(int(v) for v in tag_version.split("."))
        case _:
            raise TypeError(
                "`tag_version` must be a string or a tuple of two integers."
            )


def normalize_id3v2_tag_version(
    tag_version: str | tuple[int, int, int], /
) -> tuple[int, int, int]:
    """
    Normalize ID3v2 tag version.

    Parameters
    ----------
    tag_version : str or tuple[int, int, int]
        ID3v2 tag version.

        **Valid values**: :code:`"2.2.0"` or :code:`(2, 2, 0)`,
        :code:`"2.3.0"` or :code:`(2, 3, 0)`,
        :code:`"2.4.0"` or :code:`(2, 4, 0)`.

    Returns
    -------
    tag_version : tuple[int, int, int]
        ID3v2 tag version.
    """
    match tag_version:
        case tuple() | list():
            return tag_version
        case str():
            return tuple(int(v) for v in tag_version.split("."))
        case _:
            raise TypeError(
                "`tag_version` must be a string or a tuple of three integers."
            )

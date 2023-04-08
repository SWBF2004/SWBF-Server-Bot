MAP_IDS = \
    bes1a, bes1r, bes2a, bes2r, \
    end1a, geo1r, hot1i, kam1c, \
    kas1c, kas1i, kas2c, kas2i, \
    nab1c, nab1i, nab2a, nab2c, \
    rhn1i, rhn1r, rhn2a, rhn2c, \
    tat1i, tat1r, tat2i, tat2r, \
    yav1c, yav1i, yav2i, yav2r = range(28)

MAP_ID_NAMES = [
    "bes1a", "bes1r", "bes2a", "bes2r",
    "end1a", "geo1r", "hot1i", "kam1c",
    "kas1c", "kas1i", "kas2c", "kas2i",
    "nab1c", "nab1i", "nab2a", "nab2c",
    "rhn1i", "rhn1r", "rhn2a", "rhn2c",
    "tat1i", "tat1r", "tat2i", "tat2r",
    "yav1c", "yav1i", "yav2i", "yav2r"
]

MAP_NAMES = [
    "Bespin: Platforms GCW", "Bespin: Platforms CW", "Bespin: Cloud City GCW", "Bespin: Cloud City CW",
    "Endor: Bunker", "Geonosis: Spire", "Hoth: Echo Base", "Kamino: Tipoca City",
    "Kashyyyk: Islands CW", "Kashyyyk: Islands GCW", "Kashyyyk: Docks CW", "Kashyyyk: Docks GCW",
    "Naboo: Plains CW", "Naboo: Plains GCW", "Naboo: Theed GCW", "Naboo: Theed CW",
    "Rhen Var: Harbor GCW", "Rhen Var: Harbor CW", "Rhen Var: Citadel GCW", "Rhen Var: Citadel CW",
    "Tatooine: Dune Sea GCW", "Tatooine: Dune Sea CW", "Tatooine: Mos Eisley GCW", "Tatooine: Mos Eisley CW",
    "Yavin IV: Temple CW", "Yavin IV: Temple GCW", "Yavin IV: Arena GCW", "Yavin IV: Arena CW"
]


class Map:
    def __getitem__(self, item):
        if isinstance(item, int):
            return Map.from_id(item)
        elif isinstance(item, str):
            return Map.from_name(item)

    @staticmethod
    def from_id(map_id: int) -> str:
        return MAP_NAMES[map_id]

    @staticmethod
    def from_id_name(map_id_name: str) -> int:
        return MAP_NAMES[MAP_ID_NAMES.index(map_id_name)]

    @staticmethod
    def from_name(map_name: str) -> int:
        return MAP_NAMES.index(map_name)

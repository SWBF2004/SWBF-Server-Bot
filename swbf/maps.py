MAP_IDS = \
    unknown, \
    bes1a, bes1r, bes2a, bes2r, \
    end1a, geo1r, hot1i, kam1c, \
    kas1c, kas1i, kas2c, kas2i, \
    nab1c, nab1i, nab2a, nab2c, \
    rhn1i, rhn1r, rhn2a, rhn2c, \
    tat1i, tat1r, tat2i, tat2r, \
    yav1c, yav1i, yav2i, yav2r, \
    tat3a, tat3c, \
    ald1a, ald1c, tar1a,\
    coa1a, cor1a, cor1c,\
    dea1a, dea1c, mus1a, mus1c,\
    = range(-1, 30)

MAP_ID_NAMES = [
    "unknown",
    "bes1a", "bes1r", "bes2a", "bes2r",
    "end1a", "geo1r", "hot1i", "kam1c",
    "kas1c", "kas1i", "kas2c", "kas2i",
    "nab1c", "nab1i", "nab2a", "nab2c",
    "rhn1i", "rhn1r", "rhn2a", "rhn2c",
    "tat1i", "tat1r", "tat2i", "tat2r",
    "tat3a", "tat3c",
    "yav1c", "yav1i", "yav2i", "yav2r",
    "ald1a", "ald1c", "tar1a",
    "coa1a", "cor1a", "cor1c",
    "dea1a", "dea1c", "mus1a", "mus1c",
]

MAP_NAMES = [
    "Unkown",
    "Bespin: Platforms GCW", "Bespin: Platforms CW", "Bespin: Cloud City GCW", "Bespin: Cloud City CW",
    "Endor: Bunker", "Geonosis: Spire", "Hoth: Echo Base", "Kamino: Tipoca City",
    "Kashyyyk: Islands CW", "Kashyyyk: Islands GCW", "Kashyyyk: Docks CW", "Kashyyyk: Docks GCW",
    "Naboo: Plains CW", "Naboo: Plains GCW", "Naboo: Theed GCW", "Naboo: Theed CW",
    "Rhen Var: Harbor GCW", "Rhen Var: Harbor CW", "Rhen Var: Citadel GCW", "Rhen Var: Citadel CW",
    "Tatooine: Dune Sea GCW", "Tatooine: Dune Sea CW", "Tatooine: Mos Eisley GCW", "Tatooine: Mos Eisley CW",
    "Tatooine: Jabba's Palace GCW", "Tatooine: Jabba's Palace CW",
    "Yavin IV: Temple CW", "Yavin IV: Temple GCW", "Yavin IV: Arena GCW", "Yavin IV: Arena CW",
    "Alderaan: Castle GCW", "Alderaan: Castle CW", "Taris: Hideout GCW",
    "Ruusan: Canyon Oasis GCW", "Coruscant: Jedi Temple GCW", "Coruscant: Jedi Temple CW",
    "Deathstar: Interior GCW", "Deathstar: Interior CW", "Mustafar: Refinery GCW", "Mustafar: Refinery CW"
]


class Map:
    def __getitem__(self, item):
        if isinstance(item, int):
            return Map.from_id(item)
        elif isinstance(item, str):
            return Map.from_name(item)

    @staticmethod
    def from_id(map_id: int) -> str:
        if map_id > len(MAP_IDS):
            map_id = -1
        return MAP_NAMES[map_id]

    @staticmethod
    def from_id_name(map_id_name: str) -> int:
        return MAP_NAMES[MAP_ID_NAMES.index(map_id_name)]

    @staticmethod
    def from_name(map_name: str) -> int:
        return MAP_NAMES.index(map_name)

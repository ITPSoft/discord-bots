from enum import IntEnum, StrEnum

from common.types import ChamberRoles, BaseRoleEnum, ABCEnumMeta

ŠIMEK_NAME = "šimek#3885"
GROSSMAN_NAME = "grossmann#1086"


class Server(IntEnum):
    KOUZELNICI = 276720867344646144
    TEST_SERVER = 1420168840511492149


_DEFAULT_GIDS = frozenset(s.value for s in Server)


class Channel(IntEnum):
    """All channel IDs used by the bots"""

    # Common channels
    TWITTERPERO = 1042052161338626128
    WELCOMEPERO = 1104877855466344569

    # Šimek channels
    BOT_DEBUG_GENERAL = 1420168841501216873
    GENERAL = 1000800481397973052
    MEMES_SHITPOSTING = 324970596360257548
    BOT_TESTING = 932301697836003358
    GAMING_GENERAL = 959137743412269187
    DESKOVKY_GENERAL = 996357109727891456
    MAGIC_THE_GATHERING_GENERAL = 1370041352846573630
    PHASE_CONNECT = 786608717411647488
    MINECRAFT_GENERAL = 276720867344646144
    WARCRAFT3_GENERAL = 438037897023848448
    GACHA = 979875595896901682
    IT_PERO = 786625189038915625
    DYMKOPERO = 786643519430459423
    JIDLOPERO = 990724186550972477
    SCHIZOPERO = 998556012086829126
    KOUZELNICI_GENERAL = 941703477694955560
    ECONPOLIPERO = 786626221856391199

    # Grossmann channels
    HALL_OF_FAME = 1276805111506796605
    HOF_MEMES_THREAD = 1458175261123022848
    ROLES = 1314388851304955904
    NETHACK = 1381296005441523885
    NSFW = 276789712318889984

class VoiceChannel(IntEnum):
    ALLVOICE = 820715855397781504
    COWORKING = 1346392990754537493
    WATCHALONG = 1437931917206093845
    GEJMING_1 = 994658364174901258
    GEJMING_2 = 989180243665371156
    GEJMING_3 = 1317929148894674984
    GEJMING_5 = 1430541288574288042
    GEJMING_SMALL = 1423316251123384452
    ITPERO_VOICE = 786625367594369095

VOICE_CHANNELS_PER_SERVER = {Server.KOUZELNICI: VoiceChannel}


class TestingChannel(IntEnum):
    ILUMINATI = 1457055480747786443


KEKW = "<:kekw:940326430028488794>"

KEKW2 = "<:kekW:940324801585741844>"
KEKWR = "<:kekWR:1063089161587933204>"
PEPELA = "<:pepela:940324919739314216>"
HALL_OF_FAME_EMOJIS = [
    "⭐",
    "👍",
    "😀",
    "😃",
    "😄",
    "😁",
    "😆",
    "😅",
    "😂",
    "🤣",
    KEKW,
    KEKW2,
    KEKWR,
    PEPELA,
    "<:pog:940324188172976170>",
    "<:kekface:1097817686148386856>",
]


class SelfServiceRoles(BaseRoleEnum):
    """Seznam rolí, co si lidi sami můžou naklikat"""

    CLEN = ("Člen", 804431648959627294)
    OSTRAVAK = ("Ostravák", 988431391807131690)
    PRAZAK = ("Pražák", 998636130511630386)
    BRNAK = ("Brňák", 1105227159712309391)
    CARFAG = ("carfag", 1057281159509319800, "Carfag-péro")
    MAGIC_THE_GATHERING = ("MagicTheGathering", 1327396658605981797, "Magic The Gathering")
    KNIZNI_KLUB = ("knižní klub", 1455224895641227409, "Knižní klub")


class GamingRoles(BaseRoleEnum):
    """Seznam herních rolí pro tagy"""

    WARCRAFT = ("warcraft", 871817685439234108, "Warcraft 3")
    GMOD = ("gmod", 951457356221394975, "Garry's Mod")
    VALORANT = ("valorant", 991026818054225931, "Valorant")
    KYOUDAI = ("kyoudai", 1031510557163008010, "Kyoudai (Yakuza/Mahjong)")
    LOLKO = ("lolko", 994302892561399889, "LoL")
    DOTA2 = ("dota2", 994303445735587991, "Dota 2")
    CSGO = ("csgo", 994303566082740224, "CS:GO")
    SEA_OF_THIEVES = ("sea of thieves", 994303863643451442, "Sea of Thieves")
    MINECRAFT = ("Minecraft", 1049052005341069382)
    DARK_AND_DARKER = ("Dark and Darker", 1054111346733617222, "Dark and Darker")
    GOLFISTI = ("golfisti", 1076931268555587645, "Golf With Your Friends")
    WOWKO = ("WoWko", 1120426868697473024)
    ROCKANDSTONE = ("kámen a šutr", 1107334623983312897, "ROCK AND STONE (Deep rock Gal.)")
    HOTS = ("hots", 1140376580800118835, "Heroes of the Storm")
    GTAONLINE = ("GTA Online", 1189322955063316551)
    WARFRAME = ("Warframe", 1200135734590451834)
    HELLDIVERS = ("helldivers", 1228002980754751621, "Helldivers II")
    VOIDBOYS = ("voidboys", 1281326981878906931, "Void Crew")
    THEFINALS = ("finalnici", 1242187454837035228, "Finálníci (the Finals)")
    BEYOND_ALL_REASON = ("BeyondAllReason", 1358445521227874424, "Beyond All Reason")
    VALHEIM = ("valheim", 1356164640152883241)
    ARC_RAIDERS = ("ArcRaiders", 1432779821183930401, "Arc Raiders")
    FRIENDSLOP = ("Friendslop", 1435240483852124292)
    BAROTRAUMA = ("barotrauma", 1405232484987437106)
    TABLE_TOP_SIMULATOR = ("TabletopSimulator", 1422635058996711614, "Table Top Simulator")


class DiscordGamingTestingRoles(BaseRoleEnum):
    """Testing role enum for game pings"""

    WARCRAFT = ("warcraft", 1422634691969945830, "Warcraft 3")
    VALORANT = ("valorant", 1422634814095228928, "Valorant")


GAMING_ROLES_PER_SERVER = {Server.KOUZELNICI: GamingRoles, Server.TEST_SERVER: DiscordGamingTestingRoles}


class KouzelniciChamberRoles(ChamberRoles[BaseRoleEnum], BaseRoleEnum, metaclass=ABCEnumMeta):
    """Private-ish roles requiring access appeal poll"""

    ITPERO = ("ITPéro m o n k e", 786618350095695872, "IT Péro")
    ECONPOLIPERO = ("Ekonpolipéro", 1454177855943741492, "Ekon-poli-péro")

    def get_channel(self) -> Channel:
        match self:
            case KouzelniciChamberRoles.ITPERO:
                return Channel.IT_PERO
            case KouzelniciChamberRoles.ECONPOLIPERO:
                return Channel.ECONPOLIPERO
            case _:
                raise ValueError(f"Unknown chamber role: {self.role_name}")


class ChamberTestingRoles(ChamberRoles[BaseRoleEnum], BaseRoleEnum, metaclass=ABCEnumMeta):
    """Private-ish roles requiring access appeal poll"""

    ILUMINAT = ("Iluminát", 1457055543125475419, "Sraz iluminátů")

    def get_channel(self) -> TestingChannel:
        match self:
            case ChamberTestingRoles.ILUMINAT:
                return TestingChannel.ILUMINATI
            case _:
                raise ValueError(f"Unknown chamber role: {self.role_name}")


CHAMBER_ROLES_PER_SERVER = {Server.KOUZELNICI: KouzelniciChamberRoles, Server.TEST_SERVER: ChamberTestingRoles}


class SpecialRoles(BaseRoleEnum):
    """Single-instance role IDs for specific functionality."""

    PAUSED = ("Paused", 1449758326304014438)


class SpecialTestingRoles(BaseRoleEnum):
    PAUSED = ("Paused", 1449757350482280641)


class ListenerType(StrEnum):
    ROLEPICKER = "rolepicker"
    ANONYMPOLL = "anonympoll"
    ACCESSPOLL = "accesspoll"

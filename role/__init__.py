import typing

from LittlePaimon.database import Character
from LittlePaimon.utils import logger

from ._model import Role
from .Albedo import Albedo
from .Alhatham import Alhatham
from .Aloy import Aloy
from .Ambor import Ambor
from .Ayaka import Ayaka
from .Ayato import Ayato
from .Barbara import Barbara
from .Beidou import Beidou
from .Bennett import Bennett
from .Candace import Candace
from .Chongyun import Chongyun
from .Collei import Collei
from .Cyno import Cyno
from .Dehya import Dehya
from .Diluc import Diluc
from .Diona import Diona
from .Dori import Dori
from .Eula import Eula
from .Faruzan import Faruzan
from .Feiyan import Feiyan
from .Fischl import Fischl
from .Ganyu import Ganyu
from .Gorou import Gorou
from .Heizo import Heizo
from .Hutao import Hutao
from .Itto import Itto
from .Kaeya import Kaeya
from .Kazuha import Kazuha
from .Keqing import Keqing
from .Klee import Klee
from .Kokomi import Kokomi
from .Layla import Layla
from .Lisa import Lisa
from .Mika import Mika
from .Mona import Mona
from .Nahida import Nahida
from .Nilou import Nilou
from .Ningguang import Ningguang
from .Noel import Noel
from .PlayerElectric import PlayerElectric
from .PlayerGrass import PlayerGrass
from .PlayerRock import PlayerRock
from .PlayerWind import PlayerWind
from .Qin import Qin
from .Qiqi import Qiqi
from .Razor import Razor
from .Rosaria import Rosaria
from .Sara import Sara
from .Sayu import Sayu
from .Shenhe import Shenhe
from .Shinobu import Shinobu
from .Shougun import Shougun
from .Sucrose import Sucrose
from .Tartaglia import Tartaglia
from .Tighnari import Tighnari
from .Tohma import Tohma
from .Venti import Venti
from .Wanderer import Wanderer
from .Xiangling import Xiangling
from .Xiao import Xiao
from .Xingqiu import Xingqiu
from .Xinyan import Xinyan
from .Yae import Yae
from .Yaoyao import Yaoyao
from .Yelan import Yelan
from .Yoimiya import Yoimiya
from .Yunjin import Yunjin
from .Zhongli import Zhongli

if typing.TYPE_CHECKING:
    from ..database import CalcInfo


def get_role(
    charc: Character = None, data: "CalcInfo" = None, name: str = None
) -> Role:
    """获取角色模型"""
    if charc:
        name = charc.name
    match name:
        case x if x in ["空", "荧"]:
            match charc.element:
                case "风":
                    return PlayerWind(charc, data)
                case "岩":
                    return PlayerRock(charc, data)
                case "雷":
                    return PlayerElectric(charc, data)
                case "草":
                    return PlayerGrass(charc, data)
        case "安柏":
            return Ambor(charc, data)
        case "凯亚":
            return Kaeya(charc, data)
        case "丽莎":
            return Lisa(charc, data)
        case "芭芭拉":
            return Barbara(charc, data)
        case "雷泽":
            return Razor(charc, data)
        case "香菱":
            return Xiangling(charc, data)
        case "北斗":
            return Beidou(charc, data)
        case "行秋":
            return Xingqiu(charc, data)
        case "凝光":
            return Ningguang(charc, data)
        case "菲谢尔":
            return Fischl(charc, data)
        case "班尼特":
            return Bennett(charc, data)
        case "诺艾尔":
            return Noel(charc, data)
        case "重云":
            return Chongyun(charc, data)
        case "砂糖":
            return Sucrose(charc, data)
        case "琴":
            return Qin(charc, data)
        case "迪卢克":
            return Diluc(charc, data)
        case "七七":
            return Qiqi(charc, data)
        case "莫娜":
            return Mona(charc, data)
        case "刻晴":
            return Keqing(charc, data)
        case "温迪":
            return Venti(charc, data)
        case "可莉":
            return Klee(charc, data)
        case "迪奥娜":
            return Diona(charc, data)
        case "达达利亚":
            return Tartaglia(charc, data)
        case "辛焱":
            return Xinyan(charc, data)
        case "钟离":
            return Zhongli(charc, data)
        case "阿贝多":
            return Albedo(charc, data)
        case "甘雨":
            return Ganyu(charc, data)
        case "魈":
            return Xiao(charc, data)
        case "胡桃":
            return Hutao(charc, data)
        case "罗莎莉亚":
            return Rosaria(charc, data)
        case "烟绯":
            return Feiyan(charc, data)
        case "优菈":
            return Eula(charc, data)
        case "枫原万叶":
            return Kazuha(charc, data)
        case "神里绫华":
            return Ayaka(charc, data)
        case "早柚":
            return Sayu(charc, data)
        case "宵宫":
            return Yoimiya(charc, data)
        case "埃洛伊":
            return Aloy(charc, data)
        case "九条沙罗":
            return Sara(charc, data)
        case "雷电将军":
            return Shougun(charc, data)
        case "珊瑚宫心海":
            return Kokomi(charc, data)
        case "托马":
            return Tohma(charc, data)
        case "五郎":
            return Gorou(charc, data)
        case "荒泷一斗":
            return Itto(charc, data)
        case "云堇":
            return Yunjin(charc, data)
        case "申鹤":
            return Shenhe(charc, data)
        case "八重神子":
            return Yae(charc, data)
        case "神里绫人":
            return Ayato(charc, data)
        case "夜兰":
            return Yelan(charc, data)
        case "久岐忍":
            return Shinobu(charc, data)
        case "鹿野苑平藏":
            return Heizo(charc, data)
        case "柯莱":
            return Collei(charc, data)
        case "提纳里":
            return Tighnari(charc, data)
        case "多莉":
            return Dori(charc, data)
        case "坎蒂丝":
            return Candace(charc, data)
        case "赛诺":
            return Cyno(charc, data)
        case "妮露":
            return Nilou(charc, data)
        case "纳西妲":
            return Nahida(charc, data)
        case "莱依拉":
            return Layla(charc, data)
        case "珐露珊":
            return Faruzan(charc, data)
        case "流浪者":
            return Wanderer(charc, data)
        case "瑶瑶":
            return Yaoyao(charc, data)
        case "艾尔海森":
            return Alhatham(charc, data)
        case "迪希雅":
            return Dehya(charc, data)
        case "米卡":
            return Mika(charc, data)
    logger.info("Nahida", "➤➤", {"角色": charc.name}, "还未更新角色信息", False)
    return Role(charc, data)

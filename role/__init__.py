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

# from .Dehya import Dehya
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


def get_role(charc: Character = None) -> Role:
    """获取角色模型"""
    match charc.name:
        case x if x in ["空", "荧"]:
            match charc.element:
                case "风":
                    return PlayerWind(charc)
                case "岩":
                    return PlayerRock(charc)
                case "雷":
                    return PlayerElectric(charc)
                case "草":
                    return PlayerGrass(charc)
        case "安柏":
            return Ambor(charc)
        case "凯亚":
            return Kaeya(charc)
        case "丽莎":
            return Lisa(charc)
        case "芭芭拉":
            return Barbara(charc)
        case "雷泽":
            return Razor(charc)
        case "香菱":
            return Xiangling(charc)
        case "北斗":
            return Beidou(charc)
        case "行秋":
            return Xingqiu(charc)
        case "凝光":
            return Ningguang(charc)
        case "菲谢尔":
            return Fischl(charc)
        case "班尼特":
            return Bennett(charc)
        case "诺艾尔":
            return Noel(charc)
        case "重云":
            return Chongyun(charc)
        case "砂糖":
            return Sucrose(charc)
        case "琴":
            return Qin(charc)
        case "迪卢克":
            return Diluc(charc)
        case "七七":
            return Qiqi(charc)
        case "莫娜":
            return Mona(charc)
        case "刻晴":
            return Keqing(charc)
        case "温迪":
            return Venti(charc)
        case "可莉":
            return Klee(charc)
        case "迪奥娜":
            return Diona(charc)
        case "达达利亚":
            return Tartaglia(charc)
        case "辛焱":
            return Xinyan(charc)
        case "钟离":
            return Zhongli(charc)
        case "阿贝多":
            return Albedo(charc)
        case "甘雨":
            return Ganyu(charc)
        case "魈":
            return Xiao(charc)
        case "胡桃":
            return Hutao(charc)
        case "罗莎莉亚":
            return Rosaria(charc)
        case "烟绯":
            return Feiyan(charc)
        case "优菈":
            return Eula(charc)
        case "枫原万叶":
            return Kazuha(charc)
        case "神里绫华":
            return Ayaka(charc)
        case "早柚":
            return Sayu(charc)
        case "宵宫":
            return Yoimiya(charc)
        case "埃洛伊":
            return Aloy(charc)
        case "九条沙罗":
            return Sara(charc)
        case "雷电将军":
            return Shougun(charc)
        case "珊瑚宫心海":
            return Kokomi(charc)
        case "托马":
            return Tohma(charc)
        case "五郎":
            return Gorou(charc)
        case "荒泷一斗":
            return Itto(charc)
        case "云堇":
            return Yunjin(charc)
        case "申鹤":
            return Shenhe(charc)
        case "八重神子":
            return Yae(charc)
        case "神里绫人":
            return Ayato(charc)
        case "夜兰":
            return Yelan(charc)
        case "久岐忍":
            return Shinobu(charc)
        case "鹿野苑平藏":
            return Heizo(charc)
        case "柯莱":
            return Collei(charc)
        case "提纳里":
            return Tighnari(charc)
        case "多莉":
            return Dori(charc)
        case "坎蒂丝":
            return Candace(charc)
        case "赛诺":
            return Cyno(charc)
        case "妮露":
            return Nilou(charc)
        case "纳西妲":
            return Nahida(charc)
        case "莱依拉":
            return Layla(charc)
        case "珐露珊":
            return Faruzan(charc)
        case "流浪者":
            return Wanderer(charc)
        case "瑶瑶":
            return Yaoyao(charc)
        case "艾尔海森":
            return Alhatham(charc)
        case _:
            logger.info("Nahida", "➤➤", {"角色": charc.name}, "还未更新角色信息", False)
            return Role(charc)

from LittlePaimon.database import Character
from LittlePaimon.utils import logger

from ._model import Role
from .Ayaka import Ayaka
from .Ganyu import Ganyu
from .Klee import Klee
from .Qin import Qin
from .Venti import Venti
from .Lisa import Lisa
from .Barbara import Barbara
from .Kaeya import Kaeya
from .Ambor import Ambor


def get_role(charc: Character) -> Role:
    """获取角色模型"""
    match charc.name:
        case "安柏":
            return Ambor(charc)
        case "神里绫华":
            return Ayaka(charc)
        case "琴":
            return Qin(charc)
        case "丽莎":
            return Lisa(charc)
        case "芭芭拉":
            return Barbara(charc)
        case "凯亚":
            return Kaeya(charc)
        case "温迪":
            return Venti(charc)
        case "可莉":
            return Klee(charc)
        case "甘雨":
            return Ganyu(charc)
        case _:
            logger.info("Nahida", "➤➤", {"角色": charc.name}, "还未更新角色信息", False)
            return Role(charc)

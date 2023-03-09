from ..classmodel import BuffInfo, Info
from LittlePaimon.database import Weapon
from ..dmg_calc import DmgCalc
from .bow import Bow, Bow_setting
from .cata import Catalyst, Catalyst_setting
from .claym import Claymore, Claymore_setting
from .pole import Polearm, Polearm_setting
from .sword import Sword, Sword_setting


def weapon_buff(
    weapon: Weapon,
    buffs: list[BuffInfo],
    info: Info,
    prop: DmgCalc,
):
    match weapon.type:
        case "单手剑":
            Sword(weapon, buffs, info, prop)
        case "弓":
            Bow(weapon, buffs, info, prop)
        case "长柄":
            Polearm(weapon, buffs, info, prop)
        case "双手剑":
            Claymore(weapon, buffs, info, prop)
        case "法器":
            Catalyst(weapon, buffs, info, prop)


def weapon_setting(
    weapon: Weapon,
    info: Info,
    labels: dict,
    name: str = "",
):
    """获取武器设定"""
    match weapon.type:
        case "单手剑":
            return Sword_setting(weapon, info, labels, name)
        case "弓":
            return Bow_setting(weapon, info, labels, name)
        case "长柄":
            return Polearm_setting(weapon, info, labels, name)
        case "双手剑":
            return Claymore_setting(weapon, info, labels, name)
        case "法器":
            return Catalyst_setting(weapon, info, labels, name)
        case _:
            return []

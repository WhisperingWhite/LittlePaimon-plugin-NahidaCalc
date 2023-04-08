from LittlePaimon.database import Artifacts
from LittlePaimon.utils.genshin import GenshinTools

from .classmodel import BuffInfo, Dmg


def reserve_setting(buff_list: list[BuffInfo]):
    """保留设置"""
    labels: dict[str, str] = {}
    for buff in buff_list:
        labels |= {buff.name: buff.setting.label}
    return labels


def reserve_weight(dmg_list: list[Dmg]):
    """保留权重"""
    weights: dict[str, int] = {}
    for dmg in dmg_list:
        weights |= {dmg.name: dmg.weight}
    return weights


def reserve_exbuffs(dmg_list: list[Dmg]):
    """保留无效增益"""
    ex_buffs: dict[str, int] = {}
    for dmg in dmg_list:
        ex_buffs |= {dmg.name: dmg.exclude_buff}
    return ex_buffs


def get_relicsuit(relics: Artifacts):
    output: dict[str, int] = {}
    for suit, _ in GenshinTools.get_artifact_suit(relics):
        output.update({suit: output.get(suit, 0) + 2})
    return output


def get_rank(score: float):
    match score:
        case x if x >= 8:
            return "SSS"
        case x if x >= 7:
            return "SS"
        case x if x >= 6:
            return "S"
        case x if x >= 4:
            return "A"
        case x if x >= 2:
            return "B"
        case _:
            return "C"


def check_effective(prop_name: str, effective: list):
    match prop_name:
        case "百分比生命值":
            return "生命%" in effective
        case "生命值":
            return "生命" in effective
        case "百分比攻击力":
            return "攻击%" in effective
        case "攻击力":
            return "攻击" in effective
        case "百分比防御力":
            return "防御%" in effective
        case "防御力":
            return "防御" in effective
        case "元素精通":
            return "精通" in effective
        case "暴击率":
            return "暴击" in effective
        case "暴击伤害":
            return "暴伤" in effective
        case "治疗加成":
            return "治疗" in effective
        case "元素充能效率":
            return "充能" in effective
        case "物理伤害加成":
            return "物伤" in effective
        case "火元素伤害加成":
            return "火伤" in effective
        case "水元素伤害加成":
            return "水伤" in effective
        case "草元素伤害加成":
            return "草伤" in effective
        case "雷元素伤害加成":
            return "雷伤" in effective
        case "风元素伤害加成":
            return "风伤" in effective
        case "冰元素伤害加成":
            return "冰伤" in effective
        case "岩元素伤害加成":
            return "岩伤" in effective

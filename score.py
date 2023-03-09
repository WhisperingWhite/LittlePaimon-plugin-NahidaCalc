from copy import deepcopy

import numpy as np
from nonebot.utils import run_sync

from LittlePaimon.database import Artifact, EquipProperty

from .classmodel import Buff, BuffInfo, DmgBonus, PoFValue, RelicScore
from .role import Role

slot_dict = {
    "hp_per": 5.83,
    "hp": 298.75,
    "atk_per": 5.83,
    "atk": 19.45,
    "def_per": 7.29,
    "def": 23.15,
    "elem_ma": 23.31,
    "crit": 3.89,
    "crit_hurt": 7.77,
    "charge": 6.48,
    "heal": 4.49,
    "elem": 5.83,
    "phy": 7.29,
}
"""词条最大成长值"""

sub_prop = [
    "hp_per",
    "hp",
    "atk_per",
    "atk",
    "def_per",
    "def",
    "elem_ma",
    "crit",
    "crit_hurt",
    "charge",
]
sands_main_prop = ["hp_per", "atk_per", "def_per", "elem_ma", "charge"]
goblet_main_prop = ["hp_per", "atk_per", "def_per", "elem_ma", "elem", "phy"]
circlet_main_prop = [
    "hp_per",
    "atk_per",
    "def_per",
    "elem_ma",
    "crit",
    "crit_hurt",
    "heal",
]
element = ["pyro", "electro", "hydro", "dendro", "anemo", "geo", "cryo"]


@run_sync
def get_scores(role: Role):
    """获取圣遗物分数"""
    output = RelicScore()

    for artifact in role.artifacts.artifact_list:
        new_role = take_off_item(role, artifact)
        score = get_score(new_role, role, artifact.part)
        output.set_score(artifact.part, score)

    return output


def take_off_item(role: Role, item: Artifact):
    """脱圣遗物"""
    new_role = deepcopy(role)
    extract_prop(new_role, item.main_property)
    for sub in item.prop_list:
        extract_prop(new_role, sub)
    return new_role


def extract_prop(role: Role, slot: EquipProperty):
    """去除属性"""
    match slot.name:
        case "百分比生命值":
            role.prop.hp -= role.prop.hp * slot.value / 100
        case "生命值":
            role.prop.hp -= slot.value
        case "百分比攻击力":
            role.prop.atk -= role.prop.atk_base * slot.value / 100
        case "攻击力":
            role.prop.atk -= slot.value
        case "百分比防御力":
            role.prop.defense -= role.prop.def_base * slot.value / 100
        case "防御力":
            role.prop.defense -= slot.value
        case "元素精通":
            role.prop.elem_mastery -= slot.value
        case "暴击率":
            role.prop.crit_rate -= slot.value / 100
        case "暴击伤害":
            role.prop.crit_dmg -= slot.value / 100
        case "治疗加成":
            role.prop.healing -= slot.value / 100
        case "元素充能效率":
            role.prop.recharge -= slot.value / 100
        case "物理伤害加成":
            role.prop.elem_dmg_bonus.phy -= slot.value / 100
        case "火元素伤害加成":
            role.prop.elem_dmg_bonus.pyro -= slot.value / 100
        case "水元素伤害加成":
            role.prop.elem_dmg_bonus.hydro -= slot.value / 100
        case "草元素伤害加成":
            role.prop.elem_dmg_bonus.dendro -= slot.value / 100
        case "雷元素伤害加成":
            role.prop.elem_dmg_bonus.electro -= slot.value / 100
        case "风元素伤害加成":
            role.prop.elem_dmg_bonus.anemo -= slot.value / 100
        case "冰元素伤害加成":
            role.prop.elem_dmg_bonus.cryo -= slot.value / 100
        case "岩元素伤害加成":
            role.prop.elem_dmg_bonus.geo -= slot.value / 100


def get_score(role: Role, true_role: Role, type: str):
    """计算圣遗物分数"""
    valid_prop = role.valid_prop
    threshold = role.dmg_list[0].weight / 100
    if threshold > role.prop.recharge and "charge" not in valid_prop:
        valid_prop.append("charge")
    max_charge = max(
        np.ceil((threshold - role.prop.recharge) / (slot_dict["charge"] / 100)), 0
    )

    main_prop_list = get_main_prop(valid_prop, type)
    prop_list: list[dict[str, int]] = []
    for main_prop in main_prop_list:
        sub_props = [p for p in valid_prop if p not in main_prop and p in sub_prop]
        sub_prop_list = get_sub_prop(sub_props)
        for props in sub_prop_list:
            for i in range(6):
                for j in range(6 - i):
                    for m in range(6 - i - j):
                        for n in range(6 - i - j - m):
                            sub_prop_dist: dict[str, int] = {}
                            for idx, p in enumerate(props):
                                sub_prop_dist |= {p: [i + 1, j + 1, m + 1, n + 1][idx]}
                            if (
                                sum(sub_prop_dist.values()) == len(sub_prop_dist) + 5
                                and sub_prop_dist.get("charge", 0) <= max_charge
                            ):
                                prop_list.append(main_prop | sub_prop_dist)
    buff_list, prop_valid_list = get_buff(prop_list)

    def compens_curve(x):
        """
        充能修正曲线:\\
        y= (b-1) / ( (1+7.29/6.48*(thr-x)) * b - 1)\\
        b 为每个圣遗物预期提升\\
        目前b 取 +inf
        """
        if x < threshold:
            b = 5
            return 1 / (1 + 7.29 / slot_dict["charge"] * (threshold - x))
        return 1

    dmg_base = role.dmg()

    def calc_score(role: Role):
        dmg_list = role.dmg()
        score = 0.0
        for i, info in enumerate(dmg_list):
            if i == 0:
                continue
            if info.weight > 0:
                score += info.weight * (info.exp_value / dmg_base[i].exp_value)
        score *= compens_curve(role.prop.recharge / 100)
        return score

    base_score = calc_score(role)
    true_score = calc_score(true_role) - base_score

    max_main_score = 0.0
    for main in main_prop_list:
        (main_buff,), _ = get_buff([main])
        role_main_prop = deepcopy(role)
        role_main_prop.buffs.append(main_buff)
        main_score = calc_score(role_main_prop) - base_score
        if max_main_score < main_score:
            max_main_score = main_score

    scores = []
    max_score = 0.0
    for relic_buff in buff_list:
        role_est = deepcopy(role)
        role_est.buffs.append(relic_buff)
        est_score = calc_score(role_est) - base_score
        if max_score < est_score:
            max_score = est_score
        scores.append(est_score)

    # if type in ["生之花", "死之羽"]:
    if max_score == 0:
        return 0
    return (true_score - max_main_score) / (max_score - max_main_score) * 6
    # if true_score <= max_main_score and max_main_score != 0:
    #     return true_score / max_main_score * 2
    # else:
    #     return (true_score - max_main_score) / (max_score - max_main_score) * 4 + 2
    # return true_score / max_score * 60


def get_main_prop(valid_prop: list[str], type: str):
    """主词条"""
    output: list[dict[str, int]] = []
    match type:
        case "生之花":
            return [{"hp": 16}]
        case "死之羽":
            return [{"atk": 16}]
        case "时之沙":
            for prop in valid_prop:
                if prop in sands_main_prop:
                    output.append({prop: 8})
        case "空之杯":
            for prop in valid_prop:
                if prop in goblet_main_prop or prop in element:
                    output.append({prop: 8})
        case "理之冠":
            for prop in valid_prop:
                if prop in circlet_main_prop:
                    output.append({prop: 8})
    return output


def get_sub_prop(props: list[str]):
    """副词条"""
    if (length := len(props)) <= 4:
        return [props]

    output = []
    for i in range(length - 3):
        for j in range(i + 1, length - 2):
            for m in range(j + 1, length - 1):
                for n in range(m + 1, length):
                    output.append(
                        [
                            props[i],
                            props[j],
                            props[m],
                            props[n],
                        ]
                    )

    return output


def get_buff(props: list[dict[str, int]]):
    """生成圣遗物增益"""
    buff_list: list[list[BuffInfo]] = []
    relic_list: list[dict[str, int]] = []
    for prop in props:
        if (hp := prop.get("hp", 0)) != 16 and prop.get("hp_per", 0) != 8 and hp > 1:
            continue
        if (
            (atk := prop.get("atk", 0)) != 16
            and prop.get("atk_per", 0) != 8
            and atk > 1
        ):
            continue
        if prop.get("def_per", 0) != 8 and prop.get("def", 0) > 1:
            continue
        buff_list.append(create_buff(prop))
        relic_list.append(prop)
    return buff_list, relic_list


def create_buff(dic: dict[str, int]):
    buff = BuffInfo(
        buff_type="propbuff",
        buff=Buff(),
    )
    for key, value in dic.items():
        match key:
            case "hp":
                buff.buff.hp += PoFValue(fix=slot_dict["hp"] * value)
            case "hp_per":
                buff.buff.hp += PoFValue(percent=slot_dict["hp_per"] * value / 100)
            case "atk":
                buff.buff.atk += PoFValue(fix=slot_dict["atk"] * value)
            case "atk_per":
                buff.buff.atk += PoFValue(percent=slot_dict["atk_per"] * value / 100)
            case "def":
                buff.buff.defense += PoFValue(fix=slot_dict["def"] * value)
            case "def_per":
                buff.buff.defense += PoFValue(
                    percent=slot_dict["def_per"] * value / 100
                )
            case "elem_ma":
                buff.buff.elem_mastery += slot_dict["elem_ma"] * value
            case "crit":
                buff.buff.crit_rate += slot_dict["crit"] * value / 100
            case "crit_hurt":
                buff.buff.crit_dmg += slot_dict["crit_hurt"] * value / 100
            case "charge":
                buff.buff.recharge += slot_dict["charge"] * value / 100
            case "heal":
                buff.buff.healing += slot_dict["heal"] * value / 100
            case x if x in element:
                buff.buff.elem_dmg_bonus += DmgBonus().set(
                    {key: slot_dict["elem"] * value / 100}
                )
            case "phy":
                buff.buff.elem_dmg_bonus = DmgBonus(phy=slot_dict["phy"] * value / 100)

    return buff

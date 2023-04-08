import typing
from asyncio import run
from copy import deepcopy

from LittlePaimon.database import Artifact, EquipProperty

from .classmodel import BuffInfo, DmgBonus, PoFValue, RelicScore

if typing.TYPE_CHECKING:
    from .role import Role

slot_dict = {
    "生命%": 5.83,
    "生命": 298.75,
    "攻击%": 5.83,
    "攻击": 19.45,
    "防御%": 7.29,
    "防御": 23.15,
    "精通": 23.31,
    "暴击": 3.89,
    "暴伤": 7.77,
    "充能": 6.48,
    "治疗": 4.49,
    "元素": 5.83,
    "物伤": 7.29,
}
"""词条最大成长值"""

sub_prop = [
    "生命%",
    "生命",
    "攻击%",
    "攻击",
    "防御%",
    "防御",
    "精通",
    "暴击",
    "暴伤",
    "充能",
]
sands_main_prop = ["生命%", "攻击%", "防御%", "精通", "充能"]
goblet_main_prop = ["生命%", "攻击%", "防御%", "精通", "元素", "物伤"]
circlet_main_prop = [
    "生命%",
    "攻击%",
    "防御%",
    "精通",
    "暴击",
    "暴伤",
    "治疗",
]
element = ["火伤", "雷伤", "水伤", "草伤", "风伤", "岩伤", "冰伤"]


def get_scores(role: "Role"):
    """获取圣遗物分数"""
    output = RelicScore()

    for artifact in role.artifacts.artifact_list:
        new_role = take_off_item(role, artifact)
        score = get_score(new_role, role, artifact.part)
        output.set_score(artifact.part, score)

    return output


def take_off_item(role: "Role", item: Artifact):
    """脱圣遗物"""
    new_role = deepcopy(role)
    extract_prop(new_role, item.main_property)
    for sub in item.prop_list:
        extract_prop(new_role, sub)
    return new_role


def extract_prop(role: "Role", slot: EquipProperty):
    """去除属性"""
    match slot.name:
        case "百分比生命值":
            role.prop.hp -= role.prop.hp_base * slot.value / 100
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


def get_score(role: "Role", true_role: "Role", type: str):
    """计算圣遗物分数"""
    valid_prop = role.valid_prop
    threshold = role.dmg_list[0].weight / 100
    if threshold > role.prop.recharge and "充能" not in valid_prop:
        valid_prop.append("充能")
    # elif threshold <= role.prop.recharge and "充能" in valid_prop:
    #     valid_prop = [p for p in valid_prop if p != "充能"]
    # max_charge = max(
    #     np.ceil((threshold - role.prop.recharge) / (slot_dict["充能"] / 100)), 0
    # )

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
                                sum(sub_prop_dist.values())
                                == len(sub_prop_dist) + 5
                                # and sub_prop_dist.get("充能", 0) <= max_charge
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
            return 1 / (1 + 7.29 / slot_dict["充能"] * (threshold - x))
        return 1

    dmg_base = role.dmg()

    def calc_score(role: "Role"):
        run(role.update_buff())
        dmg_list = role.dmg()
        score = 0.0
        for i, info in enumerate(dmg_list):
            if i == 0:
                continue
            if info.weight > 0:
                score += info.weight * (info.exp_value / dmg_base[i].exp_value)
        score *= compens_curve(role.calc_recharge)
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

    if max_score == max_main_score:
        return 10
    if true_score < max_main_score:
        return 0
    return (true_score - max_main_score) / (max_score - max_main_score) * 10


def get_main_prop(valid_prop: list[str], type: str):
    """主词条"""
    output: list[dict[str, int]] = []
    match type:
        case "生之花":
            return [{"生命": 16}]
        case "死之羽":
            return [{"攻击": 16}]
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
        if (hp := prop.get("生命", 0)) != 16 and prop.get("生命%", 0) != 8 and hp > 1:
            continue
        if (atk := prop.get("攻击", 0)) != 16 and prop.get("攻击%", 0) != 8 and atk > 1:
            continue
        if prop.get("防御%", 0) != 8 and prop.get("防御", 0) > 1:
            continue
        buff_list.append(create_buff(prop))
        relic_list.append(prop)
    return buff_list, relic_list


def create_buff(dic: dict[str, int]):
    buff = BuffInfo(
        source="calc",
        buff_type="propbuff",
    )
    for key, value in dic.items():
        match key:
            case "生命":
                buff.buff.hp += PoFValue(fix=slot_dict["生命"] * value)
            case "生命%":
                buff.buff.hp += PoFValue(percent=slot_dict["生命%"] * value / 100)
            case "攻击":
                buff.buff.atk += PoFValue(fix=slot_dict["攻击"] * value)
            case "攻击%":
                buff.buff.atk += PoFValue(percent=slot_dict["攻击%"] * value / 100)
            case "防御":
                buff.buff.defense += PoFValue(fix=slot_dict["防御"] * value)
            case "防御%":
                buff.buff.defense += PoFValue(percent=slot_dict["防御%"] * value / 100)
            case "精通":
                buff.buff.elem_mastery += slot_dict["精通"] * value
            case "暴击":
                buff.buff.crit_rate += slot_dict["暴击"] * value / 100
            case "暴伤":
                buff.buff.crit_dmg += slot_dict["暴伤"] * value / 100
            case "充能":
                buff.buff.recharge += slot_dict["充能"] * value / 100
            case "治疗":
                buff.buff.healing += slot_dict["治疗"] * value / 100
            case x if x in element:
                buff.buff.elem_dmg_bonus += DmgBonus().set(
                    {key: slot_dict["元素"] * value / 100}
                )
            case "物伤":
                buff.buff.elem_dmg_bonus = DmgBonus(phy=slot_dict["物伤"] * value / 100)

    return buff

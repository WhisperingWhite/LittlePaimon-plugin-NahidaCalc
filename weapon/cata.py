from ..classmodel import Buff, BuffInfo, BuffSetting, PoFValue, FixValue, Info, DmgBonus
from LittlePaimon.database import Weapon

from ..dmg_calc import DmgCalc


def Catalyst(weapon: Weapon, buff_list: list[BuffInfo], info: Info, prop: DmgCalc):
    for buff_info in buff_list:
        setting = buff_info.setting
        match buff_info.name:
            # ============================
            # ************五星*************
            # ============================
            # 图莱杜拉的回忆
            case "图莱杜拉的回忆-堙没的蓝宝石泪滴":
                match setting.label:
                    case "1":
                        setting.state, stack = "一半层数", 0.5
                    case "2":
                        setting.state, stack = "最大层数", 1
                    case _:
                        setting.state, stack = "×", 0
                dmg_bonus = (36 + 12 * weapon.promote_level) * stack
                buff_info.buff = Buff(
                    dsc=f"普攻增伤+{dmg_bonus}",
                    target="NA",
                    dmg_bonus=dmg_bonus,
                )
            # 千夜浮梦
            case "千夜浮梦-千夜的曙歌":
                match setting.label:
                    case "0":
                        setting.state, em, dmg_bonus = (
                            "0名同色",
                            0,
                            18 + 12 * weapon.promote_level,
                        )
                    case "1":
                        setting.state, em, dmg_bonus = (
                            "1名同色",
                            24 + 8 * weapon.promote_level,
                            12 + 8 * weapon.promote_level,
                        )
                    case "2":
                        setting.state, em, dmg_bonus = (
                            "2名同色",
                            48 + 16 * weapon.promote_level,
                            6 + 4 * weapon.promote_level,
                        )
                    case _:
                        setting.state, em, dmg_bonus = (
                            "3名同色",
                            72 + 24 * weapon.promote_level,
                            0,
                        )
                buff_info.buff = Buff(
                    dsc=f"元素精通+{em}；元素增伤+{dmg_bonus}%",
                    elem_mastery=em,
                    elem_dmg_bonus=DmgBonus().set("elem", dmg_bonus),
                )
            case "千夜浮梦-千夜的曙歌(队伍)":
                em = 38 + 2 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"队友精通+{em}",
                    elem_mastery=em,
                )
            # 神乐之真意
            case "神乐之真意-神乐舞":
                match setting.label:
                    case "1":
                        setting.state, stack = "1层", 1
                    case "2":
                        setting.state, stack = "2层", 2
                    case "3":
                        setting.state, stack = "3层", 3
                    case _:
                        setting.state, stack = "×", 0
                dmg_bonus = (9 + 3 + weapon.promote_level) * stack
                buff_info.buff = Buff(
                    dsc=f"施放元素战技16秒内，元素战技增伤+{dmg_bonus}%",
                    target="E",
                    dmg_bonus=dmg_bonus,
                )
                if stack == 3:
                    dmg_bonus = 9 + 3 + weapon.promote_level
                    buff_list.append(
                        BuffInfo(
                            source=buff_info.source,
                            name="神乐之真意-神乐舞满层",
                            buff_type="propbuff",
                            buff=Buff(
                                dsc=f"神乐舞满层，元素增伤+{dmg_bonus}%",
                                elem_dmg_bonus=DmgBonus().set("elem", dmg_bonus),
                            ),
                        )
                    )
            # 不灭月华
            case "不灭月华-白夜皓月":
                dmg = prop.hp * (0.5 + 0.5 * weapon.promote_level)
                buff_info.buff = Buff(
                    dsc=f"普攻基础伤害提升生命值上限的{0.5 + 0.5 * weapon.promote_level}%(+{dmg})",
                    fix_value=FixValue(dmg=dmg),
                )
            # 尘世之锁
            case "尘世之锁-金璋皇极":
                if "1" in setting.label:
                    setting.state, stack = "1层", 1
                elif "2" in setting.label:
                    setting.state, stack = "2层", 2
                elif "3" in setting.label:
                    setting.state, stack = "3层", 3
                elif "4" in setting.label:
                    setting.state, stack = "4层", 4
                elif "5" in setting.label:
                    setting.state, stack = "5层", 5
                else:
                    setting.state, stack = "×", 0
                if "有" in setting.label:
                    setting.state += ",有护盾"
                    buff_info.buff.dsc = "护盾下，" + buff_info.buff.dsc
                    shield = 2
                else:
                    setting.state += ",无护盾"
                    shield = 1
                atk_per = (3 + 1 * weapon.promote_level) * stack * shield
                buff_info.buff.dsc += f"攻击命中8秒内，攻击+{atk_per}%(+{atk_per*prop.atk_base})"
                buff_info.buff.atk.percent = atk_per / 100
            # 四风原典
            case "四风原典-无边际的眷顾":
                match setting.label:
                    case "1":
                        setting.state, stack = "1层", 1
                    case "2":
                        setting.state, stack = "2层", 2
                    case "3":
                        setting.state, stack = "3层", 3
                    case "4":
                        setting.state, stack = "4层", 4
                    case _:
                        setting.state, stack = "×", 0
                dmg_bonus = (6 + 2 * weapon.promote_level) * stack
                buff_info.buff = Buff(
                    dsc=f"元素增伤+{dmg_bonus}%",
                    triger_type="active",
                    elem_dmg_bonus=DmgBonus().set("elem", dmg_bonus),
                )

            # ============================
            # ************四星*************
            # ============================

            # ============================
            # ************三星*************
            # ============================
        return buff_list


def Catalyst_setting(weapon: Weapon, info: Info, labels: dict, name: str):
    output: list[BuffInfo] = []

    source = f"{name}-武器"
    match weapon.name:
        # ============================
        # ************五星*************
        # ============================
        case "图莱杜拉的回忆":
            output.append(
                BuffInfo(
                    source=source,
                    name="图莱杜拉的回忆-堙没的蓝宝石泪滴",
                    setting=BuffSetting(
                        dsc=f"普攻叠层||⓪（×）：无增益；①一半层数：普攻增伤+{18+6*weapon.promote_level}；②最大层数：普攻增伤+{36+12*weapon.promote_level}",
                        label=labels.get("图莱杜拉的回忆-堙没的蓝宝石泪滴", "2"),
                    ),
                )
            )
        case "千夜浮梦":
            output.append(
                BuffInfo(
                    source=source,
                    name="千夜浮梦-千夜的曙歌",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc=f"同色元素队友的数量||⓪~③：每名同色队友精通+{24+8*weapon.promote_level}，每名异色队友元素增伤+{6+4*weapon.promote_level}%",
                        label=labels.get("千夜浮梦-千夜的曙歌", "1"),
                    ),
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="千夜浮梦-千夜的曙歌(队伍)",
                    buff_range="party",
                    buff_type="propbuff",
                )
            )
        case "神乐之真意":
            output.append(
                BuffInfo(
                    source=source,
                    name="神乐之真意-神乐舞",
                    setting=BuffSetting(
                        dsc=f"施放元素战技||⓪（×）：无增益；①~③每层：元素战技增伤+{9+3*weapon.promote_level}，"
                        + f"满层额外元素增伤+{9+3*weapon.promote_level}；",
                        label=labels.get("神乐之真意-神乐舞", "3"),
                    ),
                )
            )
        case "不灭月华":
            output.append(
                BuffInfo(
                    source=source,
                    name="不灭月华-白夜皓月",
                )
            )
        case "尘世之锁":
            output.append(
                BuffInfo(
                    source=source,
                    name="尘世之锁-金璋皇极",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc=f"攻击命中||⓪（×）：无增益；①~⑤每层：攻击力+{3+1*weapon.promote_level}%,护盾下效果翻倍",
                        label=labels.get("尘世之锁-金璋皇极", "5/有护盾"),
                    ),
                )
            )
        case "四风原典":
            output.append(
                BuffInfo(
                    source=source,
                    name="四风原典-无边际的眷顾",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc=f"站场每4秒||⓪~④每层：元素增伤+{6+2*weapon.promote_level}%",
                        label=labels.get("四风原典-无边际的眷顾", "4"),
                    ),
                )
            )
        # ============================
        # ************四星*************
        # ============================

        # ============================
        # ************三星*************
        # ============================
    return output

from ..classmodel import Buff, BuffInfo, BuffSetting, PoFValue, FixValue, Info
from LittlePaimon.database import Weapon

from ..dmg_calc import DmgCalc


def Bow(weapon: Weapon, buff_list: list[BuffInfo], info: Info, prop: DmgCalc):
    for buff_info in buff_list:
        setting = buff_info.setting
        match buff_info.name:
            # ============================
            # ************五星*************
            # ============================
            # 猎人之径
            case "猎人之径-无休止的狩猎":
                dmg = prop.elem_mastery * (120 + 40 * weapon.promote_level) / 100
                buff_info.buff = Buff(
                    dsc=f"基于精通，重击基础伤害+{dmg}",
                    target="NA",
                    fix_value=FixValue(dmg=dmg),
                )
            # 若水
            case "若水-洗濯诸类之形":
                dmg_bonus = 15 + 5 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"周围存在敌人时，增伤+{dmg_bonus}%",
                    dmg_bonus=dmg_bonus / 100,
                )
            # 冬极白星
            case "冬极白星-极昼的先兆者":
                dmg_bonus = 9 + 3 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"元素战技和元素爆发增伤+{dmg_bonus}%",
                    target=["E", "Q"],
                    dmg_bonus=dmg_bonus / 100,
                )
            case "冬极白星-白夜极星":
                match setting.label:
                    case x if x in ["1", "2", "3"]:
                        setting.state, atk_per = f"{x}层", (
                            7.5 + 2.5 * weapon.promote_level
                        ) * int(x)
                    case "4":
                        setting.state, atk_per = "4层", 36 + 12 * weapon.promote_level
                    case _:
                        setting.state, atk_per = "×", 0
                buff_info.buff = Buff(
                    dsc=f"攻击+{atk_per}%(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per / 100),
                )
            # 飞雷之弦振
            case "飞雷之弦振-飞雷御执":
                match setting.label:
                    case "1":
                        setting.state, dmg_bonus = "1层", 9 + 3 * weapon.promote_level
                    case "2":
                        setting.state, dmg_bonus = "2层", 18 + 6 * weapon.promote_level
                    case "3":
                        setting.state, dmg_bonus = "3层", 30 + 10 * weapon.promote_level
                    case _:
                        setting.state, dmg_bonus = "×", 0
                buff_info.buff = Buff(
                    dsc=f"普攻增伤+{dmg_bonus}%",
                    target="NA",
                    dmg_bonus=dmg_bonus / 100,
                )
            # 终末嗟叹之诗
            case "终末嗟叹之诗-离别的思念之歌":
                elem_ma = 75 + 25 * weapon.promote_level
                atk_per = 6 + 2 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"消耗所有追思之符，全队元素精通+{elem_ma}，攻击+{atk_per}%(+{atk_per*prop.atk_base:.0f})",
                    elem_mastery=elem_ma,
                    atk=PoFValue(percent=atk_per / 100),
                )
            # 阿莫斯之弓
            case "阿莫斯之弓-矢志不忘":
                match setting.label:
                    case x if x in ["1", "2", "3", "4", "5"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "0层", 0
                dmg_bonus = (
                    9
                    + 3 * weapon.promote_level
                    + (6 + 2 * weapon.promote_level) * stack
                )
                buff_info.buff = Buff(
                    dsc=f"普攻和重击增伤+{dmg_bonus}%",
                    target=["NA", "CA"],
                    dmg_bonus=dmg_bonus / 100,
                )
            # ============================
            # ************四星*************
            # ============================
            # 破魔之弓
            case "破魔之弓-浅濑之弭(普攻)":
                match setting.label:
                    case "1":
                        setting.state, s = "满能量", 2
                    case _:
                        setting.state, s = "缺能量", 1
                dmg_bonus = (0.12 + 0.04 * weapon.promote_level) * s
                buff_info.buff = Buff(
                    dsc=f"普攻增伤+{dmg_bonus:.0%}%",
                    target="NA",
                    dmg_bonus=dmg_bonus,
                )
            case "破魔之弓-浅濑之弭(重击)":
                match setting.label:
                    case "1":
                        setting.state, s = "满能量", 2
                    case _:
                        setting.state, s = "缺能量", 1
                dmg_bonus = (0.09 + 0.03 * weapon.promote_level) * s
                buff_info.buff = Buff(
                    dsc=f"重击增伤+{dmg_bonus:.0%}%",
                    target="CA",
                    dmg_bonus=dmg_bonus,
                )
            # ============================
            # ************三星*************
            # ============================
    return buff_list


def Bow_setting(weapon: Weapon, info: Info, labels: dict, name: str):
    output: list[BuffInfo] = []

    source = f"{name}-武器"
    match weapon.name:
        # ============================
        # ************五星*************
        # ============================
        case "猎人之径":
            output.append(
                BuffInfo(
                    source=source,
                    name="猎人之径-兽径的终点",
                )
            )
        case "若水":
            output.append(
                BuffInfo(
                    source=source,
                    name="若水-洗濯诸类之形",
                )
            )
        case "冬极白星":
            output.append(
                BuffInfo(
                    source=source,
                    name="冬极白星-极昼的先兆者",
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="冬极白星-白夜极星",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="白夜极星层数||⓪0层：无增益；①~④每层：攻击力+"
                        + f"{7.5+2.5*weapon.promote_level}/{15+5*weapon.promote_level}/"
                        + f"{22.5+7.5*weapon.promote_level}/{36+12*weapon.promote_level}%",
                        label=labels.get("冬极白星-白夜极星", "4"),
                    ),
                )
            )
        case "飞雷之弦振":
            output.append(
                BuffInfo(
                    source=source,
                    name="飞雷之弦振-飞雷御执",
                    setting=BuffSetting(
                        dsc="飞雷之巴印层数||⓪0层：无增益；①~③每层：普攻增伤+"
                        + f"{9+3*weapon.promote_level}/{18+6*weapon.promote_level}/"
                        + f"{30+10*weapon.promote_level}%",
                        label=labels.get("飞雷之弦振-飞雷御执", "3"),
                    ),
                )
            )
        case "终末嗟叹之诗":
            output.append(
                BuffInfo(
                    source=source,
                    name="终末嗟叹之诗-离别的思念之歌",
                    buff_range="all",
                    buff_type="propbuff",
                )
            )
        case "阿莫斯之弓":
            output.append(
                BuffInfo(
                    source=source,
                    name="阿莫斯之弓-矢志不忘",
                    setting=BuffSetting(
                        dsc="箭矢发射后每0.1秒||⓪0层：基础增益；"
                        + f"①~⑤每层：增伤+{6+2*weapon.promote_level}%",
                        label=labels.get("阿莫斯之弓-矢志不忘", "5"),
                    ),
                )
            )
        # ============================
        # ************四星*************
        # ============================
        case "破魔之弓":
            output.append(
                BuffInfo(
                    source=source,
                    name="破魔之弓-浅濑之弭(普攻)",
                    setting=BuffSetting(
                        dsc="①元素能量满时，效果提升1倍",
                        label=labels.get("破魔之弓-浅濑之弭(普攻)", "1"),
                    ),
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="破魔之弓-浅濑之弭(重击)",
                    setting=BuffSetting(
                        dsc="①元素能量满时，效果提升1倍",
                        label=labels.get("破魔之弓-浅濑之弭(重击)", "1"),
                    ),
                )
            )
        # ============================
        # ************三星*************
        # ============================
    return output

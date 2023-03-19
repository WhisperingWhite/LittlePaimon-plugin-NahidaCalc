from LittlePaimon.database import Weapon

from ..classmodel import Buff, BuffInfo, BuffSetting, Info, PoFValue
from ..dmg_calc import DmgCalc


def Claymore(weapon: Weapon, buff_list: list[BuffInfo], info: Info, prop: DmgCalc):
    for buff_info in buff_list:
        setting = buff_info.setting
        match buff_info.name:
            # ============================
            # ************五星*************
            # ============================
            # 息灾
            case "息灾-灭却之戒法":
                buff_info.buff = Buff(
                    dsc=f"基于充能，攻击+{atk_per:.1%}%(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            # 薙草之稻光
            case "薙草之稻光-非时之梦，常世灶食(攻击提升)":
                atk_per = (prop.recharge - 1) * (0.21 + 0.07 * weapon.promote_level)
                buff_info.buff = Buff(
                    dsc=f"基于充能，攻击+{atk_per:.1%}%(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "薙草之稻光-非时之梦，常世灶食(充能提升)":
                recharge = 0.25 + 0.05 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"施放元素爆发后的12秒内，充能+{recharge:.0%}%",
                    recharge=recharge,
                )
            # 护摩之杖
            case "护摩之杖-无羁的朱赤之蝶":
                match setting.label:
                    case "1":
                        setting.state, atk = (
                            "半血以下",
                            (1.4 + 0.4 * weapon.promote_level) * prop.hp,
                        )
                    case _:
                        setting.state, atk = (
                            "半血以上",
                            (0.6 + 0.2 * weapon.promote_level) * prop.hp,
                        )
                buff_info.buff = Buff(
                    dsc=f"基于生命，攻击+{atk}",
                    atk=PoFValue(fix=atk),
                )
            # 贯虹之槊
            case "贯虹之槊-金璋皇极":
                label1, label2 = setting.label.split("/")
                match label1:
                    case x if x in ["1", "2", "3", "4", "5"]:
                        setting.state, s = f"{x}层", int(x)
                    case _:
                        setting.state, s = "×", 0
                if "有" in label2:
                    setting.state += "/有护盾"
                    shield = 2
                    buff_info.buff.dsc = "护盾下，"
                else:
                    setting.state += "/无护盾"
                    shield = 1
                atk_per = (0.03 + 0.01 * weapon.promote_level) * s * shield
                buff_info.buff.dsc += (
                    f"攻击命中8秒内，攻击+{atk_per:.0%}% (+{atk_per*prop.atk_base:.0f})",
                )
                buff_info.buff.atk = PoFValue(percent=atk_per)
            # 和璞鸢
            case "和璞鸢-昭理的鸢之枪":
                match setting.label:
                    case x if x in ["1", "2", "3", "4", "5", "6", "7"]:
                        setting.state, s = f"{x}层", int(x)
                    case _:
                        setting.state, s = "×", 0
                atk_per = s * (2.5 + 0.7 * weapon.promote_level)
                dmg_bonus = 9 + 3 * weapon.promote_level if s == 7 else 0
                buff_info.buff = Buff(
                    dsc=f"{setting.state}，攻击+{atk_per:.1f}%({atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                    dmg_bonus=dmg_bonus,
                )
                if dmg_bonus != 0:
                    buff_info.buff.dsc += f"，增伤+{dmg_bonus}%"
        # ============================
        # ************四星*************
        # ============================

        # ============================
        # ************三星*************
        # ============================

    return buff_list


def Claymore_setting(weapon: Weapon, info: Info, labels: dict, name: str):
    output: list[BuffInfo] = []

    source = f"{name}-武器"
    match weapon.name:
        # ============================
        # ************五星*************
        # ============================
        case "赤沙之杖":
            output.append(
                BuffInfo(
                    source=source,
                    name="赤沙之杖-蜃气尽头的热梦",
                    buff_type="transbuff",
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="赤沙之杖-赤沙之梦",
                    buff_type="transbuff",
                    setting=BuffSetting(
                        dsc="元素战技命中叠层，最大三层（①~③）",
                        label=labels.get("赤沙之杖-赤沙之梦", "1"),
                    ),
                )
            )
        case "息灾":
            output.append(
                BuffInfo(
                    source=source,
                    name="息灾-灭却之戒法",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="①处于后台时，效果翻倍",
                        label=labels.get("息灾-灭却之戒法", "1"),
                    ),
                )
            )
        case "薙草之稻光":
            output.append(
                BuffInfo(
                    source=source,
                    name="薙草之稻光-非时之梦，常世灶食(攻击提升)",
                    buff_type="transbuff",
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="薙草之稻光-非时之梦，常世灶食(充能提升)",
                    buff_type="propbuff",
                )
            )
        case "护摩之杖":
            output.append(
                BuffInfo(
                    source=source,
                    name="护摩之杖-无羁的朱赤之蝶",
                    buff_type="transbuff",
                    setting=BuffSetting(
                        dsc=f"⓪半血以上（×）：攻击力提升生命上限的{0.6+0.2*weapon.promote_level}%；"
                        + f"①半血以下（✓）：攻击力提升生命上限的{1.4+0.4*weapon.promote_level}%",
                        label=labels.get("护摩之杖-无羁的朱赤之蝶", "1"),
                    ),
                )
            )
        case "贯虹之槊":
            output.append(
                BuffInfo(
                    source=source,
                    name="贯虹之槊-金璋皇极",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc=f"攻击命中叠层，①~⑤每层攻击+{3+1*weapon.promote_level}%，护盾下效果翻倍",
                        label=labels.get("贯虹之槊-金璋皇极", "5/有护盾"),
                    ),
                )
            )
        case "和璞鸢":
            output.append(
                BuffInfo(
                    source=source,
                    name="和璞鸢-昭理的鸢之枪",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc=f"命中后叠层，①~⑦每层：攻击+{2.5+0.7*weapon.promote_level}%，满层额外增伤+{9+3*weapon.promote_level}%",
                        label=labels.get("和璞鸢-昭理的鸢之枪", "7"),
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

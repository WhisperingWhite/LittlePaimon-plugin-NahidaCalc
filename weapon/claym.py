from ..classmodel import Buff, BuffInfo, BuffSetting, PoFValue, Info
from LittlePaimon.database import Weapon

from ..dmg_calc import DmgCalc


def Claymore(weapon: Weapon, buff_list: list[BuffInfo], info: Info, prop: DmgCalc):
    for buff_info in buff_list:
        setting = buff_info.setting
        # ============================
        # ************五星*************
        # ============================
        # 和璞鸢
        if buff_info.name == "和璞鸢·昭理的鸢之枪":
            if setting.label == "0":
                setting.state = "×"
                continue
            elif setting.label == "1":
                setting.state, stack = "1层", 1
            elif setting.label == "2":
                setting.state, stack = "2层", 2
            elif setting.label == "3":
                setting.state, stack = "3层", 3
            elif setting.label == "4":
                setting.state, stack = "4层", 4
            elif setting.label == "5":
                setting.state, stack = "5层", 5
            elif setting.label == "6":
                setting.state, stack = "6层", 6
            else:
                setting.state, stack = "7层", 7
            atk_per = stack * (2.5 + 0.7 * weapon.affix)
            dmg_bonus = 9 + 3 * weapon.affix if stack == 7 else 0
            buff_info.buff = Buff(
                dsc=f"攻击+{atk_per}% => {atk_per*prop.atk_base}",
                atk=PoFValue(percent=atk_per),
                dmg_bonus=dmg_bonus,
            )
            if dmg_bonus != 0:
                buff_info.buff.dsc += f"；增伤+{dmg_bonus}%"
        # 贯虹之槊
        if buff_info.name == "贯虹之槊·金璋皇极":
            if "0" in setting.label:
                setting.state = "×"
                continue
            elif "1" in setting.label:
                setting.state, stack = "1层", 1
            elif "2" in setting.label:
                setting.state, stack = "2层", 2
            elif "3" in setting.label:
                setting.state, stack = "3层", 3
            elif "4" in setting.label:
                setting.state, stack = "4层", 4
            else:
                setting.state, stack = "5层", 5
            if "无" in setting.label:
                setting.state += "/无"
                shield = 1
            else:
                setting.state += "/护盾"
                shield = 2
            atk_per = (3 + 1 * weapon.affix) * stack * shield
            buff_info.buff = Buff(
                dsc=f"攻击命中8秒内，攻击+{atk_per}% => {atk_per*prop.atk_base}",
                atk=PoFValue(percent=atk_per / 100),
            )
            if shield == 2:
                buff_info.buff.dsc = "护盾下，" + buff_info.buff.dsc
        # 护摩之杖
        if buff_info.name == "护摩之杖·无羁的朱赤之蝶":
            if setting.label == "0":
                setting.state, atk = "半血以上", (0.6 + 0.2 * weapon.affix) * prop.hp
            else:
                setting.state, atk = "半血以下", (1.4 + 0.4 * weapon.affix) * prop.hp
            buff_info.buff = Buff(
                dsc=f"攻击力+{atk}",
                atk=PoFValue(fix=atk),
            )
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
    # ============================
    # ************五星*************
    # ============================
    if weapon.name == "和璞鸢":
        output.append(
            BuffInfo(
                source=source,
                name="和璞鸢·昭理的鸢之枪",
                buff_type="propbuff",
                setting=BuffSetting(
                    dsc=f"命中后6秒||⓪~⑦每层：攻击+{2.5+0.7*weapon.affix}%，满层增伤+{9+3*weapon.affix}",
                    label=labels.get("和璞鸢·昭理的鸢之枪", "7"),
                ),
            )
        )
    if weapon.name == "贯虹之槊":
        output.append(
            BuffInfo(
                source=source,
                name="贯虹之槊·金璋皇极",
                buff_type="propbuff",
                setting=BuffSetting(
                    dsc=f"攻击命中||⓪（×）：无增益；①~⑤每层：护盾下，攻击力+{3+1*weapon.affix}%；"
                    + "无：-；护盾：效果翻倍",
                    label=labels.get("贯虹之槊·金璋皇极", "5/护盾"),
                ),
            )
        )
    if weapon.name == "护摩之杖":
        output.append(
            BuffInfo(
                source=source,
                name="护摩之杖·无羁的朱赤之蝶",
                buff_type="transbuff",
                setting=BuffSetting(
                    dsc=f"是否半血以下||⓪半血以上（×）：攻击力提升生命上限的{0.6+0.2*weapon.affix}%；"
                    + f"①半血以下（✓）：攻击力提升生命上限的{1.4+0.4*weapon.affix}%",
                    label=labels.get("护摩之杖·无羁的朱赤之蝶", "1"),
                ),
            )
        )
    if weapon.name == "薙草之稻光":
        output.append(
            BuffInfo(
                source=source,
                name="薙草之稻光·非时之梦，常世灶食",
                buff_type="transbuff",
                setting=BuffSetting(
                    dsc=f"是否半血以下||⓪半血以上（×）：攻击力提升生命上限的{0.6+0.2*weapon.affix}%；"
                    + f"①半血以下（✓）：攻击力提升生命上限的{1.4+0.4*weapon.affix}%",
                    label=labels.get("薙草之稻光·非时之梦，常世灶食", "1"),
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

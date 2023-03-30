from LittlePaimon.database import Weapon

from ..classmodel import Buff, BuffInfo, BuffSetting, Info, PoFValue
from ..dmg_calc import DmgCalc


def Polearm(weapon: Weapon, buff_list: list[BuffInfo], info: Info, prop: DmgCalc):
    for buff_info in buff_list:
        setting = buff_info.setting
        match buff_info.name:
            # ============================
            # ************五星*************
            # ============================
            case "赤沙之杖-蜃气尽头的热梦":
                match setting.label:
                    case n if n in ["1", "2", "3"]:
                        setting.state, stack = f"{n}层", int(n)
                    case _:
                        setting.state, stack = "0层", 0
                per = (
                    0.39
                    + 0.13 * weapon.affix_level
                    + (0.21 + 0.07 * weapon.affix_level) * stack
                )
                atk = per * prop.elem_mastery
                buff_info.buff = Buff(
                    dsc=f"{setting.state}「赤沙之梦」，基于精通{per:.0%}，攻击+{atk:.0f}",
                    atk=PoFValue(fix=atk),
                )
            # 息灾
            case "息灾-灭却之戒法":
                match setting.label.split("/"):
                    case n, s if n in ["1", "2", "3", "4", "5", "6"] and s in [
                        "0",
                        "1",
                    ]:
                        stack, pos = int(n), int(s) + 1
                        setting.state = f"{n}层「圆顿」，在后台" if pos == 2 else f"{n}层「圆顿」，在前台"
                    case _:
                        setting.state, stack, pos = "×", 0, 0
                atk_per = (0.024 + 0.008 * weapon.affix_level) * stack * pos
                buff_info.buff = Buff(
                    dsc=f"{setting.state}，攻击+{atk_per:.1%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            # 薙草之稻光
            case "薙草之稻光-非时之梦，常世灶食(攻击提升)":
                per = 0.21 + 0.07 * weapon.affix_level
                atk_per = min(per * (prop.recharge - 1), 0.7 + 0.1 * weapon.affix_level)
                buff_info.buff = Buff(
                    dsc=f"基于充能的{per:.0%}，攻击+{atk_per:.1%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "薙草之稻光-非时之梦，常世灶食(充能提升)":
                recharge = 0.25 + 0.05 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"施放元素爆发后的12秒内，充能+{recharge:.0%}",
                    recharge=recharge,
                )
            # 护摩之杖
            case "护摩之杖-无羁的朱赤之蝶":
                match setting.label:
                    case "1":
                        setting.state, per = (
                            "半血以下",
                            0.014 + 0.004 * weapon.affix_level,
                        )
                    case _:
                        setting.state, per = (
                            "半血以上",
                            0.006 + 0.002 * weapon.affix_level,
                        )
                atk = per * prop.hp
                buff_info.buff = Buff(
                    dsc=f"{setting.state}，基于生命{per:.1%}，攻击+{atk:.0f}",
                    atk=PoFValue(fix=atk),
                )
            # 贯虹之槊
            case "贯虹之槊-金璋皇极":
                match setting.label.split("/"):
                    case n, s if n in ["1", "2", "3", "4", "5"] and s in ["0", "1"]:
                        stack, shield = int(n), int(s) + 1
                        setting.state = f"{n}层，有护盾" if shield == 2 else f"{n}层，无护盾"
                    case _:
                        setting.state, stack, shield = "×", 0, 0
                atk_per = (0.03 + 0.01 * weapon.affix_level) * stack * shield
                buff_info.buff = Buff(
                    dsc=f"{setting.state}，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            # 和璞鸢
            case "和璞鸢-昭理的鸢之枪":
                match setting.label:
                    case n if n in ["1", "2", "3", "4", "5", "6", "7"]:
                        setting.state, stack = f"{n}层", int(n)
                    case _:
                        setting.state, stack = "×", 0
                atk_per = (0.025 + 0.07 * weapon.affix_level) * stack
                dmg_bonus = 0.09 + 0.03 * weapon.affix_level if stack == 7 else 0
                buff_info.buff = Buff(
                    dsc=f"{setting.state}，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                    dmg_bonus=dmg_bonus,
                )
                if stack == 7:
                    buff_info.buff.dsc += f"，满层增伤+{dmg_bonus:.0%}"
            # ============================
            # ************四星*************
            # ============================
            case "风信之锋-不至之风":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.09 + 0.03 * weapon.affix_level
                elem_ma = 36 + 12 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"触发元素反应10秒内，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})，精通+{elem_ma}",
                    atk=PoFValue(percent=atk_per),
                    elem_mastery=elem_ma,
                )
            case "贯月矢-幽林月影":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.12 + 0.04 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"拾取苏生之叶12秒内，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "断浪长鳍-驭浪的海祇民":
                setting.state, stack = "×", 0
                if setting.label.isdigit():
                    if (n := int(setting.label)) <= 360:
                        setting.state, stack = f"{n}点能量上限", n
                dmg_bonus = min(
                    (0.09 + 0.03 * weapon.affix_level) * stack,
                    0.3 + 0.1 * weapon.affix_level,
                )
                buff_info.buff = Buff(
                    dsc=f"{setting.state}，元素爆发增伤+{dmg_bonus:.0%}",
                    target="Q",
                    dmg_bonus=dmg_bonus,
                )
            case "「渔获」-船歌":
                dmg_bonus = 0.12 + 0.04 * weapon.affix_level
                crit_rate = 0.045 + 0.015 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"元素爆发增伤+{dmg_bonus:.0%}，暴击+{crit_rate:.0%}",
                    target="Q",
                    dmg_bonus=dmg_bonus,
                    crit_rate=crit_rate,
                )
            case "喜多院十文字-名士振舞":
                dmg_bonus = 0.045 + 0.015 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"元素战技增伤+{dmg_bonus:.0%}",
                    target="E",
                    dmg_bonus=dmg_bonus,
                )
            case "千岩长枪-千岩诀·同心":
                match setting.label:
                    case n if n in ["1", "2", "3", "4"]:
                        setting.state, stack = f"{n}名", int(n)
                    case _:
                        setting.state, stack = "×", 0
                atk_per = (0.06 + 0.01 * weapon.affix_level) * stack
                crit_rate = (0.02 + 0.01 * weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}璃月角色，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})，暴击+{crit_rate:.0%}",
                    atk=PoFValue(percent=atk_per),
                    crit_rate=crit_rate,
                )
            case "决斗之枪-角斗士":
                match setting.label:
                    case "1":
                        setting.state = "至少两名"
                        per = 0.12 + 0.04 * weapon.affix_level
                        buff_info.buff = Buff(
                            dsc=f"身边至少两名敌人，攻击+{per:.0%}(+{per*prop.atk_base:.0f})，防御+{per:.0%}(+{per*prop.def_base:.0f})",
                            atk=PoFValue(percent=per),
                            defense=PoFValue(percent=per),
                        )
                    case _:
                        setting.state = "少于两名"
                        atk_per = 0.18 + 0.06 * weapon.affix_level
                        buff_info.buff = Buff(
                            dsc=f"身边少于两名敌人，攻击+{per:.0%}(+{per*prop.atk_base:.0f})",
                            atk=PoFValue(percent=per),
                        )
            case "黑岩刺枪-乘胜追击":
                match setting.label:
                    case n if n in ["1", "2", "3"]:
                        setting.state, stack = f"{n}层", int(n)
                    case _:
                        setting.state, stack = "×", 0
                atk_per = (0.12 + 0.03 * weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})，持续30秒，每层独立",
                    atk=PoFValue(percent=atk_per),
                )
            case "试作星镰-嗜魔":
                match setting.label:
                    case n if n in ["1", "2"]:
                        setting.state, stack = f"{n}层", int(n)
                    case _:
                        setting.state, stack = "×", 0
                dmg_bonus = (0.06 + 0.02 * weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，普攻、重击增伤+{dmg_bonus:.0%}，持续12秒",
                    target=["NA", "CA"],
                    dmg_bonus=dmg_bonus,
                )
            case "匣里灭辰-踏火止水":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.16 + 0.04 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"对水或火附着下的敌人，增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            # ============================
            # ************三星*************
            # ============================
            case "白缨枪-锐利":
                dmg_bonus = 0.18 + 0.06 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"普攻增伤+{dmg_bonus:.0%}",
                    target="NA",
                    dmg_bonus=dmg_bonus,
                )
    return buff_list


def Polearm_setting(weapon: Weapon, info: Info, labels: dict, name: str):
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
                    setting=BuffSetting(
                        dsc="元素战技命中叠层，①~③每层基于精通，提升攻击，最大3层",
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
                        dsc="施放元素战技后随时间叠层，①~⑥每层提升攻击，最大6层/⓪处于前台；①处于后台时，效果翻倍",
                        label=labels.get("息灾-灭却之戒法", "6/1"),
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
                        dsc="⓪半血以上；①半血以下：基于生命上限提升攻击",
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
                        dsc="攻击命中叠层，①~⑤每层提升攻击/⓪无护盾；①护盾下效果翻倍",
                        label=labels.get("贯虹之槊-金璋皇极", "5/1"),
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
                        dsc="命中后叠层，①~⑦每层提升攻击，满层时提升额外增伤，最大7层",
                        label=labels.get("和璞鸢-昭理的鸢之枪", "7"),
                    ),
                )
            )
        # ============================
        # ************四星*************
        # ============================
        case "风信之锋":
            output.append(
                BuffInfo(
                    source=source,
                    name="风信之锋-不至之风",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("风信之锋-不至之风", "○")),
                )
            )
        case "贯月矢":
            output.append(
                BuffInfo(
                    source=source,
                    name="贯月矢-幽林月影",
                    buff_range="all",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("贯月矢-幽林月影", "○")),
                )
            )
        case "断浪长鳍":
            output.append(
                BuffInfo(
                    source=source,
                    name="断浪长鳍-驭浪的海祇民",
                    setting=BuffSetting(
                        dsc="队伍中每点元素能量，增加元素爆发增伤" + f"增伤上限{30+10*weapon.affix_level}%",
                        label=labels.get("断浪长鳍-驭浪的海祇民", "320"),
                    ),
                )
            )
        case "「渔获」":
            output.append(
                BuffInfo(
                    source=source,
                    name="「渔获」-船歌",
                )
            )
        case "喜多院十文字":
            output.append(
                BuffInfo(
                    source=source,
                    name="喜多院十文字-名士振舞",
                )
            )
        case "千岩长枪":
            output.append(
                BuffInfo(
                    source=source,
                    name="千岩长枪-千岩诀·同心",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="队伍中每位璃月角色，①~④提升攻击与暴击，最大4层",
                        label=labels.get("千岩长枪-千岩诀·同心", "4"),
                    ),
                )
            )
        case "决斗之枪":
            output.append(
                BuffInfo(
                    source=source,
                    name="决斗之枪-角斗士",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="身边敌人⓪少于两名①至少两名",
                        label=labels.get("决斗之枪-角斗士", "0"),
                    ),
                )
            )
        case "黑岩刺枪":
            output.append(
                BuffInfo(
                    source=source,
                    name="黑岩刺枪-乘胜追击",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="击杀叠层，①~③每层提升攻击，持续时间独立",
                        label=labels.get("黑岩刺枪-乘胜追击", "3"),
                    ),
                )
            )
        case "试作星镰":
            output.append(
                BuffInfo(
                    source=source,
                    name="试作星镰-嗜魔",
                    setting=BuffSetting(
                        dsc="施放元素战技叠层，①~②每层提升普攻、重击增伤，最大2层",
                        label=labels.get("试作星镰-嗜魔", "2"),
                    ),
                )
            )
        case "匣里灭辰":
            output.append(
                BuffInfo(
                    source=source,
                    name="匣里灭辰-踏火止水",
                    setting=BuffSetting(label=labels.get("匣里灭辰-踏火止水", "○")),
                )
            )
        # ============================
        # ************三星*************
        # ============================
        case "白缨枪":
            output.append(
                BuffInfo(
                    source=source,
                    name="白缨枪-锐利",
                )
            )
    return output

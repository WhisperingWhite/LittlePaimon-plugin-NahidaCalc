from LittlePaimon.database import Weapon

from ..classmodel import Buff, BuffInfo, BuffSetting, Info, Multiplier, PoFValue
from ..dmg_calc import DmgCalc


def Claymore(weapon: Weapon, buff_list: list[BuffInfo], info: Info, prop: DmgCalc):
    for buff_info in buff_list:
        setting = buff_info.setting
        match buff_info.name:
            # ============================
            # ************五星*************
            # ============================
            case "苇海信标-沙海守望":
                match setting.label.split("/"):
                    case n1, n2, n3 if n1 in ["0", "1"] and n2 in ["0", "1"] and n3 in [
                        "0",
                        "1",
                    ]:
                        atk_per = (0.15 + 0.05 * weapon.promote_level) * (
                            int(n1) + int(n2)
                        )
                        hp_per = (0.24 + 0.08 * weapon.promote_level) * int(n3)
                        setting.state = f"触发{int(n1)+int(n2)}种效果"
                        if n3 == "1":
                            setting.state += "，无护盾"
                        else:
                            setting.state += "，有护盾"
                    case _:
                        setting.state, atk_per, hp_per = "×", 0, 0
                buff_info.buff = Buff(
                    dsc=f"{setting.state}，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})"
                    + f"生命上限+{hp_per:.0%}(+{hp_per*prop.hp_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                    hp=PoFValue(percent=hp_per),
                )
            case "赤角石溃杵-御伽大王御伽话":
                scaler = 0.3 + 0.1 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"普攻、重击倍率+{scaler:.0%}防御",
                    target=["NA", "CA"],
                    multiplier=Multiplier(defense=scaler),
                )
            case "松籁响起之时-揭旗的叛逆之歌":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.15 + 0.05 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"消耗所有低语之符，全队攻击+{atk_per:.0%}，持续12秒",
                    atk=PoFValue(percent=atk_per),
                )
            case "无工之剑-金璋皇极":
                match setting.label.split("/"):
                    case n, s if n in ["1", "2", "3", "4", "5"] and s in ["0", "1"]:
                        stack, shield = int(n), int(s) + 1
                        setting.state = f"{n}层，有护盾" if shield == 2 else f"{n}层，无护盾"
                    case _:
                        setting.state, stack, shield = "×", 0, 0
                atk_per = (0.03 + 0.01 * weapon.promote_level) * stack * shield
                buff_info.buff = Buff(
                    dsc=f"{setting.state}，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "狼的末路-如狼般狩猎者":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.3 + 0.1 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"消命中生命低于30%的敌人12秒内，全队攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            # ============================
            # ************四星*************
            # ============================
            case "饰铁之花-风与花的密语":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.12 + 0.03 * weapon.promote_level
                elem_ma = 36 + 12 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"元素战技命中或触发元素反应12秒内，全队攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})，精通+{elem_ma}",
                    atk=PoFValue(percent=atk_per),
                    elem_mastery=elem_ma,
                )
            case "玛海菈的水色-沙上楼阁":
                percent = 0.18 + 0.06 * weapon.promote_level
                atk = prop.elem_mastery * percent
                buff_info.buff = Buff(
                    dsc=f"基于精通的{percent:.0%}，攻击+({atk:.0f})",
                    atk=PoFValue(fix=atk),
                )
            case "玛海菈的水色-沙上楼阁(队友)":
                percent = 0.18 + 0.06 * weapon.promote_level
                atk = prop.elem_mastery * percent * 0.3
                buff_info.buff = Buff(
                    dsc=f"队友攻击+{atk:.0f}",
                    atk=PoFValue(fix=atk),
                )
            case "森林王器-森林的瑞佑":
                if setting.label == "-":
                    setting.state = "×"
                elem_ma = 45 + 15 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"拾取种识之叶12秒内，精通+{elem_ma}",
                    elem_mastery=elem_ma,
                )
            case "恶王丸-驭浪的海祇民":
                setting.state, stack = "×", 0
                if setting.label.isdigit():
                    if (n := int(setting.label)) <= 360:
                        setting.state, stack = f"{n}点能量上限", n
                dmg_bonus = min(
                    (0.09 + 0.03 * weapon.promote_level) * stack,
                    0.3 + 0.1 * weapon.promote_level,
                )
                buff_info.buff = Buff(
                    dsc=f"{setting.state}，元素爆发增伤+{dmg_bonus:.0%}",
                    target="Q",
                    dmg_bonus=dmg_bonus,
                )
            case "衔珠海皇-海洋的胜利":
                dmg_bonus = 0.09 + 0.03 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"元素爆发增伤+{dmg_bonus:.0%}",
                    target="Q",
                    dmg_bonus=dmg_bonus,
                )
            case "桂木斩长正-名士振舞":
                dmg_bonus = 0.045 + 0.015 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"元素战技增伤+{dmg_bonus:.0%}",
                    target="E",
                    dmg_bonus=dmg_bonus,
                )
            case "千岩古剑-千岩诀·同心":
                match setting.label:
                    case n if n in ["1", "2", "3", "4"]:
                        setting.state, stack = f"{n}名", int(n)
                    case _:
                        setting.state, stack = "×", 0
                atk_per = (0.06 + 0.01 * weapon.promote_level) * stack
                crit_rate = (0.02 + 0.01 * weapon.promote_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}璃月角色，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})，暴击+{crit_rate:.0%}",
                    atk=PoFValue(percent=atk_per),
                    crit_rate=crit_rate,
                )
            case "螭骨剑-破浪":
                match setting.label:
                    case n if n in ["1", "2", "3", "4", "5"]:
                        setting.state, stack = f"{n}层", int(n)
                    case _:
                        setting.state, stack = "×", 0
                dmg_bonus = (0.05 + 0.01 * weapon.promote_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，增伤{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            case "黑岩斩刀-乘胜追击":
                match setting.label:
                    case n if n in ["1", "2", "3"]:
                        setting.state, stack = f"{n}层", int(n)
                    case _:
                        setting.state, stack = "×", 0
                atk_per = (0.12 + 0.03 * weapon.promote_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})，持续30秒，每层独立",
                    atk=PoFValue(percent=atk_per),
                )
            case "白影剑-注能之锋":
                match setting.label:
                    case n if n in ["1", "2", "3", "4"]:
                        setting.state, stack = f"{n}层", int(n)
                    case _:
                        setting.state, stack = "×", 0
                per = (0.045 + 0.015 * weapon.promote_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，攻击+{per:.0%}(+{per*prop.atk_base:.0f})，防御+{per:.0%}(+{per*prop.def_base:.0f})，持续6秒",
                    atk=PoFValue(percent=per),
                    defense=PoFValue(percent=per),
                )
            case "雨裁-止水息雷":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.16 + 0.04 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"敌方水或雷附着，增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            # ============================
            # ************三星*************
            # ============================
            case "飞天大御剑-勇气":
                match setting.label:
                    case n if n in ["1", "2", "3", "4"]:
                        setting.state, stack = f"{n}层", int(n)
                    case _:
                        setting.state, stack = "×", 0
                atk_per = (0.05 + 0.01 * weapon.promote_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})，持续6秒",
                    atk=PoFValue(percent=atk_per),
                )
            case "沐浴龙血的剑-踏火息雷":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.09 + 0.03 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"敌方火或雷附着，增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            case "铁影阔剑-不屈":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.25 + 0.05 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"生命低于70%时，重击增伤+{dmg_bonus:.0%}",
                    target="CA",
                    dmg_bonus=dmg_bonus,
                )
    return buff_list


def Claymore_setting(weapon: Weapon, info: Info, labels: dict, name: str):
    output: list[BuffInfo] = []
    source = f"{name}-武器"
    match weapon.name:
        # ============================
        # ************五星*************
        # ============================
        case "苇海信标":
            output.append(
                BuffInfo(
                    source=source,
                    name="苇海信标-沙海守望",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="①元素战技命中，提升攻击/①收到伤害时，提升攻击/①不处于护盾庇护，提高生命上限",
                        label=labels.get("苇海信标-沙海守望", "1/1/1"),
                    ),
                )
            )
        case "赤角石溃杵":
            output.append(
                BuffInfo(
                    source=source,
                    name="赤角石溃杵-御伽大王御伽话",
                )
            )
        case "松籁响起之时":
            output.append(
                BuffInfo(
                    source=source,
                    name="松籁响起之时-揭旗的叛逆之歌",
                    buff_range="all",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("松籁响起之时-揭旗的叛逆之歌", "○")),
                )
            )
        case "无工之剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="无工之剑-金璋皇极",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="攻击命中叠层，①~⑤每层提升攻击/⓪无护盾；①护盾下效果翻倍",
                        label=labels.get("无工之剑-金璋皇极", "5/1"),
                    ),
                )
            )
        case "狼的末路":
            output.append(
                BuffInfo(
                    source=source,
                    name="狼的末路-如狼般狩猎者",
                    buff_range="all",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("狼的末路-如狼般狩猎者", "○")),
                )
            )
        # ============================
        # ************四星*************
        # ============================
        case "饰铁之花":
            output.append(
                BuffInfo(
                    source=source,
                    name="饰铁之花-风与花的密语",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("饰铁之花-风与花的密语", "○")),
                )
            )
        case "玛海菈的水色":
            output.append(
                BuffInfo(
                    source=source,
                    name="玛海菈的水色-沙上楼阁",
                    buff_type="transbuff",
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="玛海菈的水色-沙上楼阁(队友)",
                    buff_range="party",
                    buff_type="transbuff",
                )
            )
        case "森林王器":
            output.append(
                BuffInfo(
                    source=source,
                    name="森林王器-森林的瑞佑",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("森林王器-森林的瑞佑", "○")),
                )
            )
        case "恶王丸":
            output.append(
                BuffInfo(
                    source=source,
                    name="恶王丸-驭浪的海祇民",
                    setting=BuffSetting(
                        dsc="队伍中每点元素能量，增加元素爆发增伤，"
                        + f"增伤上限{30+10*weapon.promote_level}%",
                        label=labels.get("恶王丸-驭浪的海祇民", "320"),
                    ),
                )
            )
        case "衔珠海皇":
            output.append(
                BuffInfo(
                    source=source,
                    name="衔珠海皇-海洋的胜利",
                )
            )
        case "桂木斩长正":
            output.append(
                BuffInfo(
                    source=source,
                    name="桂木斩长正-名士振舞",
                )
            )
        case "千岩古剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="千岩古剑-千岩诀·同心",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="队伍中每位璃月角色，①~④提升攻击与暴击，最大4层",
                        label=labels.get("千岩古剑-千岩诀·同心", "4"),
                    ),
                )
            )
        case "螭骨剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="螭骨剑-破浪",
                    setting=BuffSetting(
                        dsc="角色站场且不受伤叠层，①~⑤每层提升增伤，最大5层",
                        label=labels.get("螭骨剑-破浪", "5"),
                    ),
                )
            )
        case "黑岩斩刀":
            output.append(
                BuffInfo(
                    source=source,
                    name="黑岩斩刀-乘胜追击",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="击杀叠层，①~③每层提升攻击，持续时间独立",
                        label=labels.get("黑岩斩刀-乘胜追击", "3"),
                    ),
                )
            )
        case "白影剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="白影剑-注能之锋",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="普攻和重击命中叠层，①~④每层提升攻击和防御，最大4层",
                        label=labels.get("白影剑-注能之锋", "4"),
                    ),
                )
            )
        case "雨裁":
            output.append(
                BuffInfo(
                    source=source,
                    name="雨裁-止水息雷",
                    setting=BuffSetting(label=labels.get("雨裁-止水息雷", "○")),
                )
            )
        # ============================
        # ************三星*************
        # ============================
        case "飞天大御剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="飞天大御剑-勇气",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="普攻和重击命中叠层，①~④每层提升攻击，最大4层",
                        label=labels.get("飞天大御剑-勇气", "4"),
                    ),
                )
            )
        case "沐浴龙血的剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="沐浴龙血的剑-踏火息雷",
                    setting=BuffSetting(label=labels.get("沐浴龙血的剑-踏火息雷", "○")),
                )
            )
        case "铁影阔剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="铁影阔剑-不屈",
                    setting=BuffSetting(label=labels.get("铁影阔剑-不屈", "○")),
                )
            )
    return output

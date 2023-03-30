from LittlePaimon.database import Weapon

from ..classmodel import Buff, BuffInfo, BuffSetting, Info, Multiplier, PoFValue
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
                if setting.label == "-":
                    setting.state = "×"
                scaler = 120 + 40 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"重击倍率+{scaler}%精通",
                    target="CA",
                    multiplier=Multiplier(em=scaler),
                )
            # 若水
            case "若水-洗濯诸类之形":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.15 + 0.05 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"周围存在敌人时，增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            # 冬极白星
            case "冬极白星-极昼的先兆者":
                dmg_bonus = 0.09 + 0.03 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"元素战技和元素爆发增伤+{dmg_bonus:.0%}",
                    target=["E", "Q"],
                    dmg_bonus=dmg_bonus,
                )
            case "冬极白星-白夜极星":
                match setting.label:
                    case x if x in ["1", "2", "3"]:
                        setting.state, atk_per = (
                            f"{x}层",
                            (0.075 + 0.025 * weapon.affix_level) * int(x),
                        )
                    case "4":
                        setting.state, atk_per = (
                            "4层",
                            0.36 + 0.12 * weapon.affix_level,
                        )
                    case _:
                        setting.state, atk_per = "×", 0
                buff_info.buff = Buff(
                    dsc=f"白夜极星{setting.state}，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            # 飞雷之弦振
            case "飞雷之弦振-飞雷御执":
                match setting.label:
                    case x if x in ["1", "2"]:
                        setting.state, dmg_bonus = (
                            f"{x}层",
                            (0.09 + 0.03 * weapon.affix_level) * int(x),
                        )
                    case "3":
                        setting.state, dmg_bonus = (
                            "3层",
                            0.3 + 0.1 * weapon.affix_level,
                        )
                    case _:
                        setting.state, dmg_bonus = "×", 0
                buff_info.buff = Buff(
                    dsc=f"飞雷之巴印{setting.state}，普攻增伤+{dmg_bonus:.0%}",
                    target="NA",
                    dmg_bonus=dmg_bonus,
                )
            # 终末嗟叹之诗
            case "终末嗟叹之诗-离别的思念之歌":
                if setting.label == "-":
                    setting.state = "×"
                elem_ma = 75 + 25 * weapon.affix_level
                atk_per = 0.06 + 0.02 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"消耗所有追思之符时，全队元素精通+{elem_ma}，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    elem_mastery=elem_ma,
                    atk=PoFValue(percent=atk_per),
                )
            # 阿莫斯之弓
            case "阿莫斯之弓-矢志不忘":
                match setting.label:
                    case x if x in ["1", "2", "3", "4", "5"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "0层", 0
                dmg_bonus = (
                    0.09
                    + 0.03 * weapon.affix_level
                    + (0.06 + 0.02 * weapon.affix_level) * stack
                )
                buff_info.buff = Buff(
                    dsc=f"{setting.state}箭矢，普攻和重击增伤+{dmg_bonus:.0%}",
                    target=["NA", "CA"],
                    dmg_bonus=dmg_bonus,
                )
            # ============================
            # ************四星*************
            # ============================
            # 王下近侍
            case "王下近侍-迷宫之王的教导":
                if setting.label == "-":
                    setting.state = "×"
                elem_ma = 40 + 20 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"施放元素战技或元素爆发12秒内，精通+{elem_ma}",
                    elem_mastery=elem_ma,
                )
            # 落霞
            case "落霞-渊中霞彩":
                match setting.label:
                    case "1":
                        setting.state, dmg_bonus = (
                            "夕暮",
                            4.5 + 1.5 * weapon.affix_level,
                        )
                    case "2":
                        setting.state, dmg_bonus = (
                            "流霞",
                            7.5 + 2.5 * weapon.affix_level,
                        )
                    case _:
                        setting.state, dmg_bonus = (
                            "朝晖",
                            10.5 + 3.5 * weapon.affix_level,
                        )
                buff_info.buff = Buff(
                    dsc=f"{setting.state}状态下，增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            # 朦云之月
            case "朦云之月-驭浪的海祇民":
                setting.state, stack = "×", 0
                if setting.label.isdigit():
                    if (x := int(setting.label)) <= 360:
                        setting.state, stack = f"{x}点能量上限", x
                dmg_bonus = min(
                    (0.09 + 0.03 * weapon.affix_level) * stack,
                    0.3 + 0.1 * weapon.affix_level,
                )
                buff_info.buff = Buff(
                    dsc=f"{setting.state}，元素爆发增伤+{dmg_bonus:.0%}",
                    target="Q",
                    dmg_bonus=dmg_bonus,
                )
            # 破魔之弓
            case "破魔之弓-浅濑之弭(普攻)":
                match setting.label:
                    case "1":
                        setting.state, stack = "满能量", 2
                    case _:
                        setting.state, stack = "缺能量", 1
                dmg_bonus = (0.12 + 0.04 * weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}时，普攻增伤+{dmg_bonus:.0%}",
                    target="NA",
                    dmg_bonus=dmg_bonus,
                )
            case "破魔之弓-浅濑之弭(重击)":
                match setting.label:
                    case "1":
                        setting.state, stack = "满能量", 2
                    case _:
                        setting.state, stack = "缺能量", 1
                dmg_bonus = (0.09 + 0.03 * weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}时，重击增伤+{dmg_bonus:.0%}",
                    target="CA",
                    dmg_bonus=dmg_bonus,
                )
            # 幽夜华尔兹
            case "幽夜华尔兹-极夜二重奏":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.15 + 0.05 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"普攻命中5秒内，元素战技增伤+{dmg_bonus:.0%}，"
                    + f"元素战技命中5秒内，普攻增伤+{dmg_bonus:.0%}",
                    target=["NA", "E"],
                    dmg_bonus=dmg_bonus,
                )
            # 风花之颂
            case "风花之颂-风花之愿":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.12 + 0.04 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"施放元素战技6秒内，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            # 暗巷猎手
            case "暗巷猎手-街巷伏击":
                setting.state, stack = "×", 0
                if setting.label.isdigit():
                    if 1 <= (x := int(setting.label)) <= 10:
                        setting.state, stack = f"{x}层", x
                dmg_bonus = 0.02 * weapon.affix_level * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            # 黑岩战弓
            case "黑岩战弓-乘胜追击":
                match setting.label:
                    case x if x in ["1", "2", "3"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "×", 0
                atk_per = (0.09 + 0.03 * weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})，持续30秒，每层独立",
                    atk=PoFValue(percent=atk_per),
                )
            # 钢轮弓
            case "钢轮弓-注能之矢":
                match setting.label:
                    case x if x in ["1", "2", "3", "4"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "×", 0
                atk_per = (0.03 + 0.01 * weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})，持续6秒",
                    atk=PoFValue(percent=atk_per),
                )
            # 试做澹月
            case "试做澹月-离簇不归":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.27 + 0.09 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"重击命中要害10秒内，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            # 弓藏
            case "弓藏-速射弓斗(普攻)":
                dmg_bonus = 0.3 + 0.1 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"普攻增伤+{dmg_bonus:.0%}",
                    target="NA",
                    dmg_bonus=dmg_bonus,
                )
            case "弓藏-速射弓斗(重击)":
                buff_info.buff = Buff(
                    dsc="重击增伤-10%",
                    target="CA",
                    dmg_bonus=-0.1,
                )
            # 绝弦
            case "绝弦-无矢之歌":
                dmg_bonus = 0.18 + 0.06 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"元素战技与元素爆发增伤+{dmg_bonus:.0%}",
                    target=["E", "Q"],
                    dmg_bonus=dmg_bonus,
                )
            # ============================
            # ************三星*************
            # ============================
            # 弹弓
            case "弹弓-弹弓(增伤)":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.3 + 0.06 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"普攻与重击的箭矢在发射0.3秒内命中，增伤+{dmg_bonus:.0%}",
                    target=["NA", "CA"],
                    dmg_bonus=dmg_bonus,
                )
            case "弹弓-弹弓(减伤)":
                if setting.label == "-":
                    setting.state = "×"
                buff_info.buff = Buff(
                    dsc="普攻与重击的箭矢在发射0.3秒后命中，增伤-10%",
                    target=["NA", "CA"],
                    dmg_bonus=-0.1,
                )
            # 神射手之誓
            case "神射手之誓-精准":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.18 + 0.06 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"针对要害的攻击增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            # 鸦羽弓
            case "鸦羽弓-踏火止水":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.09 + 0.03 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"对水或火附着下的敌人，增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
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
                    setting=BuffSetting(label=labels.get("猎人之径-兽径的终点", "○")),
                )
            )
        case "若水":
            output.append(
                BuffInfo(
                    source=source,
                    name="若水-洗濯诸类之形",
                    setting=BuffSetting(label=labels.get("若水-洗濯诸类之形", "○")),
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
                        dsc="白夜极星层数，①~④每层提升攻击力，最大4层",
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
                        dsc="飞雷之巴印层数，①~③每层提升普攻增伤，最大3层",
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
                    setting=BuffSetting(label=labels.get("终末嗟叹之诗-离别的思念之歌", "○")),
                )
            )
        case "阿莫斯之弓":
            output.append(
                BuffInfo(
                    source=source,
                    name="阿莫斯之弓-矢志不忘",
                    setting=BuffSetting(
                        dsc="箭矢发射后每0.1秒叠层，①~⑤每层提升增伤，最大5层",
                        label=labels.get("阿莫斯之弓-矢志不忘", "5"),
                    ),
                )
            )
        # ============================
        # ************四星*************
        # ============================
        case "王下近侍":
            output.append(
                BuffInfo(
                    source=source,
                    name="王下近侍-迷宫之王的教导",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("王下近侍-迷宫之王的教导", "○")),
                )
            )
        case "落霞":
            output.append(
                BuffInfo(
                    source=source,
                    name="落霞-渊中霞彩",
                    setting=BuffSetting(
                        dsc="①夕暮；②流霞；③朝晖，三种状态提升不同增伤",
                        label=labels.get("落霞-渊中霞彩", "3"),
                    ),
                )
            )
        case "朦云之月":
            output.append(
                BuffInfo(
                    source=source,
                    name="朦云之月-驭浪的海祇民",
                    setting=BuffSetting(
                        dsc="队伍中每点元素能量，增加元素爆发增伤，" + f"增伤上限{30+10*weapon.affix_level}%",
                        label=labels.get("朦云之月-驭浪的海祇民", "320"),
                    ),
                )
            )
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
        case "幽夜华尔兹":
            output.append(
                BuffInfo(
                    source=source,
                    name="幽夜华尔兹-极夜二重奏",
                    setting=BuffSetting(label=labels.get("幽夜华尔兹-极夜二重奏", "○")),
                )
            )
        case "风花之颂":
            output.append(
                BuffInfo(
                    source=source,
                    name="风花之颂-风花之愿",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("风花之颂-风花之愿", "○")),
                )
            )
        case "暗巷猎手":
            output.append(
                BuffInfo(
                    source=source,
                    name="暗巷猎手-街巷伏击",
                    setting=BuffSetting(
                        dsc=f"处于后台叠层，①~⑩每层增加增伤，增伤上限{10*weapon.affix_level}%",
                        label=labels.get("暗巷猎手-街巷伏击", "10"),
                    ),
                )
            )
        case "黑岩战弓":
            output.append(
                BuffInfo(
                    source=source,
                    name="黑岩战弓-乘胜追击",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="击杀叠层，①~③每层增加攻击，最大3层",
                        label=labels.get("黑岩战弓-乘胜追击", "3"),
                    ),
                )
            )
        case "钢轮弓":
            output.append(
                BuffInfo(
                    source=source,
                    name="钢轮弓-注能之矢",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="普攻和重击命中叠层，①~④每层增加攻击，最大4层",
                        label=labels.get("钢轮弓-注能之矢", "4"),
                    ),
                )
            )
        case "试做澹月":
            output.append(
                BuffInfo(
                    source=source,
                    name="试做澹月-离簇不归",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("试做澹月-离簇不归", "○")),
                )
            )
        case "弓藏":
            output.append(
                BuffInfo(
                    source=source,
                    name="弓藏-速射弓斗(普攻)",
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="弓藏-速射弓斗(重击)",
                )
            )
        case "绝弦":
            output.append(
                BuffInfo(
                    source=source,
                    name="绝弦-无矢之歌",
                )
            )
        # ============================
        # ************三星*************
        # ============================
        case "弹弓":
            output.append(
                BuffInfo(
                    source=source,
                    name="弹弓-弹弓(增伤)",
                    setting=BuffSetting(label=labels.get("弹弓-弹弓(增伤)", "○")),
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="弹弓-弹弓(减伤)",
                    setting=BuffSetting(label=labels.get("弹弓-弹弓(减伤)", "-")),
                )
            )
        case "神射手之誓":
            output.append(
                BuffInfo(
                    source=source,
                    name="神射手之誓-精准",
                    setting=BuffSetting(label=labels.get("神射手之誓-精准", "○")),
                )
            )
        case "鸦羽弓":
            output.append(
                BuffInfo(
                    source=source,
                    name="鸦羽弓-踏火止水",
                    setting=BuffSetting(label=labels.get("鸦羽弓-踏火止水", "○")),
                )
            )
    return output

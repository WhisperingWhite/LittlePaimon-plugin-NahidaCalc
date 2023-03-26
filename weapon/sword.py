from LittlePaimon.database import Weapon

from ..classmodel import (
    Buff,
    BuffInfo,
    BuffSetting,
    DmgBonus,
    Info,
    Multiplier,
    PoFValue,
)
from ..dmg_calc import DmgCalc


def Sword(weapon: Weapon, buff_list: list[BuffInfo], info: Info, prop: DmgCalc):
    for buff_info in buff_list:
        setting = buff_info.setting
        match buff_info.name:
            # ============================
            # ************五星*************
            # ============================
            case "裁叶萃光-白月枝芒":
                scaler = 90 + 30 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"普攻、元素战技倍率+{scaler}%精通",
                    target=["NA", "E"],
                    multiplier=Multiplier(em=scaler),
                )
            case "圣显之钥-沉入沙海的史诗":
                match setting.label:
                    case n if n in ["1", "2", "3"]:
                        setting.state, stack = f"{n}层", int(n)
                    case _:
                        setting.state, stack = "×", 0
                per = (0.0009 + 0.0003 * weapon.promote_level) * stack
                elem_ma = per * prop.hp
                buff_info.buff = Buff(
                    dsc=f"{setting.state}「宏大诗篇」，基于生命上限{per:.2%}，精通+{elem_ma:.0f}",
                    elem_mastery=elem_ma,
                )
            case "圣显之钥-沉入沙海的史诗满层":
                if setting.label == "-":
                    setting.state = "×"
                per = 0.0015 + 0.0005 * weapon.promote_level
                elem_ma = per * prop.hp
                buff_info.buff = Buff(
                    dsc=f"触发「宏大诗篇」20秒内，基于生命上限{per:.2%}，全队精通+{elem_ma:.0f}",
                    elem_mastery=elem_ma,
                )
            case "波乱月白经津-白刃流转":
                match setting.label:
                    case n if n in ["1", "2"]:
                        setting.state, stack = f"{n}层", int(n)
                    case _:
                        setting.state, stack = "×", 0
                dmg_bonus = (0.015 + 0.05 * weapon.promote_level) * stack
                buff_info.buff = Buff(
                    dsc=f"消耗{setting.state}「波穗」，普攻增伤+{dmg_bonus:.0%}，持续8秒",
                    target="NA",
                    dmg_bonus=dmg_bonus,
                )
            case "雾切之回光-雾切御腰物":
                match setting.label:
                    case n if n in ["1", "2"]:
                        setting.state, dmg_bonus = f"{n}层", (
                            0.06 + 0.02 * weapon.promote_level
                        ) * int(n)
                    case "3":
                        setting.state, dmg_bonus = (
                            "3层",
                            0.21 + 0.07 * weapon.promote_level,
                        )
                    case _:
                        setting.state, dmg_bonus = "×", 0
                buff_info.buff = Buff(
                    dsc=f"持有{setting.state}雾切之巴印，自身类型元素增伤+{dmg_bonus:.0%}",
                    elem_dmg_bonus=DmgBonus().set({f"{info.element}": dmg_bonus}),
                )
            case "苍古自由之誓-抗争的践行之歌":
                dmg_bonus = 0.075 + 0.025 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            case "磐岩结绿-护国的无垢之心":
                if setting.label == "-":
                    setting.state = "×"
                per = 0.012 + 0.003 * weapon.promote_level
                atk = per * prop.hp_base
                buff_info.buff = Buff(
                    dsc=f"基于生命上限{per:.1%}，攻击+{atk:.0f}",
                    atk=PoFValue(fix=atk),
                )
            case "斫峰之刃-金璋皇极":
                match setting.label.split("/"):
                    case n, s if n in ["1", "2", "3", "4", "5"] and s in ["0", "1"]:
                        stack, shield = int(n), int(s) + 1
                        setting.state = "{n}层，有护盾" if shield == 2 else "{n}层，无护盾"
                    case _:
                        setting.state, stack, shield = "×", 0, 0
                atk_per = (0.03 + 0.01 * weapon.promote_level) * stack * shield
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            # ============================
            # ************四星*************
            # ============================
            case "东花坊时雨-怪谭·时雨心地一本足":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.12 + 0.04 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"给敌人施加「纸伞作祟」，对敌人增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            case "西福斯的月光-镇灵的低语":
                percent = (0.027 + 0.009 * weapon.promote_level) / 100
                recharge = prop.elem_mastery * percent
                buff_info.buff = Buff(
                    dsc=f"基于精通的{percent:.3%}，充能+{recharge:.0%}",
                    recharge=recharge,
                )
            case "西福斯的月光-镇灵的低语(队友)":
                percent = (0.027 + 0.009 * weapon.promote_level) / 100
                recharge = prop.elem_mastery * percent * 0.3
                buff_info.buff = Buff(
                    dsc=f"队友充能+{recharge:.0%}",
                    recharge=recharge,
                )
            case "原木刀-森林的瑞佑":
                if setting.label == "-":
                    setting.state = "×"
                elem_ma = 45 + 15 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"拾取种识之叶12秒内，精通+{elem_ma}",
                    elem_mastery=elem_ma,
                )
            case "笼钓瓶一心-澄澄一心传":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.15
                buff_info.buff = Buff(
                    dsc=f"普攻、重击或下落命中8秒内，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "辰砂之纺锤-无垢之心":
                scaler = 30 + 10 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"元素战技倍率+{scaler}%防御力",
                    target="E",
                    multiplier=Multiplier(defense=scaler),
                )
            case "暗巷闪光-街巷游侠":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.09 + 0.03 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            case "腐殖之剑-无尽的渴慕":
                dmg_bonus = 0.12 + 0.04 * weapon.promote_level
                crit_rate = 0.045 + 0.015 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"元素战技增伤+{dmg_bonus:.0%}，暴击+{crit_rate:.1%}",
                    target="E",
                    dmg_bonus=dmg_bonus,
                    crit_rate=crit_rate,
                )
            case "黑剑-「正义」":
                dmg_bonus = 0.15 + 0.05 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"普攻与重击增伤+{dmg_bonus:.0%}",
                    target=["NA", "CA"],
                    dmg_bonus=dmg_bonus,
                )
            case "黑岩长剑-乘胜追击":
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
            case "铁蜂刺-注能之刺":
                match setting.label:
                    case n if n in ["1", "2"]:
                        setting.state, stack = f"{n}层", int(n)
                    case _:
                        setting.state, stack = "×", 0
                dmg_bonus = (0.045 + 0.015 * weapon.promote_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，增伤+{dmg_bonus:.1%}，持续6秒",
                    dmg_bonus=dmg_bonus,
                )
            case "匣里龙吟-踏火息雷":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.16 + 0.04 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"敌方火或雷附着，增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            # ============================
            # ************三星*************
            # ============================
            case "飞天御剑-决心":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.09 + 0.03 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"施放元素爆发15秒内，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "暗铁剑-过载":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.15 + 0.05 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"触发雷反应（结晶除外）12秒内，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "黎明神剑-激励":
                if setting.label == "-":
                    setting.state = "×"
                crit_rate = 0.115 + 0.035 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"生命高于90%时，暴击+{crit_rate:.1%}",
                    crit_rate=crit_rate,
                )
            case "冷刃-止水融冰":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.09 + 0.03 * weapon.promote_level
                buff_info.buff = Buff(
                    dsc=f"敌方水或冰附着，增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
    return buff_list


def Sword_setting(weapon: Weapon, info: Info, labels: dict, name: str):
    output: list[BuffInfo] = []
    source = f"{name}-武器"
    match weapon.name:
        # ============================
        # ************五星*************
        # ============================
        case "裁叶萃光":
            output.append(
                BuffInfo(
                    source=source,
                    name="裁叶萃光-白月枝芒",
                )
            )
        case "圣显之钥":
            output.append(
                BuffInfo(
                    source=source,
                    name="圣显之钥-沉入沙海的史诗",
                    buff_type="transbuff",
                    setting=BuffSetting(
                        dsc="元素战技命中叠层，①~③每层提升精通，满层提升额外队伍精通",
                        label=labels.get("圣显之钥-沉入沙海的史诗", "3"),
                    ),
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="圣显之钥-沉入沙海的史诗满层",
                    buff_range="all",
                    buff_type="transbuff",
                    setting=BuffSetting(label=labels.get("圣显之钥-沉入沙海的史诗满层", "○")),
                )
            )
        case "波乱月白经津":
            output.append(
                BuffInfo(
                    source=source,
                    name="波乱月白经津-白刃流转",
                    setting=BuffSetting(
                        dsc="消耗「波穗」效果，①~②每层提升普攻增伤，最多2层",
                        label=labels.get("波乱月白经津-白刃流转", "2"),
                    ),
                )
            )
        case "雾切之回光":
            output.append(
                BuffInfo(
                    source=source,
                    name="雾切之回光-雾切御腰物",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="叠加「雾切之巴印」①~③每层提升元素增伤，最多3层",
                        label=labels.get("雾切之回光-雾切御腰物", "3"),
                    ),
                )
            )
        case "苍古自由之誓":
            output.append(
                BuffInfo(
                    source=source,
                    name="苍古自由之誓-抗争的践行之歌",
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="苍古自由之誓-千年的大乐章·揭旗之歌",
                    buff_range="all",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("苍古自由之誓-千年的大乐章·揭旗之歌", "○")),
                )
            )
        case "磐岩结绿":
            output.append(
                BuffInfo(
                    source=source,
                    buff_type="transbuff",
                    name="磐岩结绿-护国的无垢之心",
                )
            )
        case "斫峰之刃":
            output.append(
                BuffInfo(
                    source=source,
                    name="斫峰之刃-金璋皇极",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="攻击命中叠层，①~⑤每层提升攻击/⓪无护盾；①护盾下效果翻倍",
                        label=labels.get("斫峰之刃-金璋皇极", "5/1"),
                    ),
                )
            )
        # ============================
        # ************四星*************
        # ============================
        case "东花坊时雨":
            output.append(
                BuffInfo(
                    source=source,
                    name="东花坊时雨-怪谭·时雨心地一本足",
                    setting=BuffSetting(label=labels.get("东花坊时雨-怪谭·时雨心地一本足", "○")),
                )
            )
        case "西福斯的月光":
            output.append(
                BuffInfo(
                    source=source,
                    name="西福斯的月光-镇灵的低语",
                    buff_type="transbuff",
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="西福斯的月光-镇灵的低语(队友)",
                    buff_range="party",
                    buff_type="transbuff",
                )
            )
        case "原木刀":
            output.append(
                BuffInfo(
                    source=source,
                    name="原木刀-森林的瑞佑",
                    buff_range="all",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("原木刀-森林的瑞佑", "○")),
                )
            )
        case "笼钓瓶一心":
            output.append(
                BuffInfo(
                    source=source,
                    name="笼钓瓶一心-澄澄一心传",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("笼钓瓶一心-澄澄一心传", "○")),
                )
            )
        case "辰砂之纺锤":
            output.append(
                BuffInfo(
                    source=source,
                    name="辰砂之纺锤-无垢之心",
                )
            )
        case "暗巷闪光":
            output.append(
                BuffInfo(
                    source=source,
                    name="暗巷闪光-街巷游侠",
                    setting=BuffSetting(label=labels.get("暗巷闪光-街巷游侠", "○")),
                )
            )
        case "腐殖之剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="腐殖之剑-无尽的渴慕",
                )
            )
        case "黑剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="黑剑-「正义」",
                )
            )
        case "黑岩长剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="黑岩长剑-乘胜追击",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="击杀叠层，①~③每层提升攻击，持续时间独立",
                        label=labels.get("黑岩长剑-乘胜追击", "3"),
                    ),
                )
            )
        case "铁蜂刺":
            output.append(
                BuffInfo(
                    source=source,
                    name="铁蜂刺-注能之刺",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="造成元素伤害叠层，①~②每层提升增伤，最大2层",
                        label=labels.get("铁蜂刺-注能之刺", "2"),
                    ),
                )
            )
        case "匣里龙吟":
            output.append(
                BuffInfo(
                    source=source,
                    name="匣里龙吟-踏火息雷",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("匣里龙吟-踏火息雷", "○")),
                )
            )
        # ============================
        # ************三星*************
        # ============================
        case "飞天御剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="飞天御剑-决心",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("飞天御剑-决心", "○")),
                )
            )
        case "暗铁剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="暗铁剑-过载",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("暗铁剑-过载", "○")),
                )
            )
        case "黎明神剑":
            output.append(
                BuffInfo(
                    source=source,
                    name="黎明神剑-激励",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("黎明神剑-激励", "○")),
                )
            )
        case "冷刃":
            output.append(
                BuffInfo(
                    source=source,
                    name="冷刃-止水融冰",
                    setting=BuffSetting(label=labels.get("冷刃-止水融冰", "○")),
                )
            )
    return output

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
                dmg_bonus = (0.36 + 0.12 * weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"达到{setting.state}时，普攻增伤+{dmg_bonus:.0%}",
                    target="NA",
                    dmg_bonus=dmg_bonus,
                )
            # 千夜浮梦
            case "千夜浮梦-千夜的曙歌":
                match setting.label:
                    case x if x in ["1", "2", "3"]:
                        setting.state, em, dmg_bonus = (
                            f"{x}名同元素",
                            (24 + 8 * weapon.affix_level) * (3 - int(x)),
                            (0.06 + 0.04 * weapon.affix_level) * int(x),
                        )
                    case _:
                        setting.state, em, dmg_bonus = (
                            "0名同元素",
                            0,
                            0.18 + 0.12 * weapon.affix_level,
                        )
                buff_info.buff = Buff(
                    dsc=f"队伍中有{setting.state}，元素精通+{em}，元素增伤+{dmg_bonus:.0%}",
                    elem_mastery=em,
                    elem_dmg_bonus=DmgBonus().set("elem", dmg_bonus),
                )
            case "千夜浮梦-千夜的曙歌(队伍)":
                em = 38 + 2 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"队友精通+{em}",
                    elem_mastery=em,
                )
            # 神乐之真意
            case "神乐之真意-神乐舞":
                match setting.label:
                    case x if x in ["1", "2", "3"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "×", 0
                dmg_bonus = (0.09 + 0.03 + weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"施放元素战技16秒内，元素战技增伤+{dmg_bonus:.0%}",
                    target="E",
                    dmg_bonus=dmg_bonus,
                )
            case "神乐之真意-神乐舞满层":
                dmg_bonus = 0.09 + 0.03 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"神乐舞满层，元素增伤+{dmg_bonus:.0%}",
                    elem_dmg_bonus=DmgBonus().set("elem", dmg_bonus),
                )
            # 不灭月华
            case "不灭月华-白夜皓月":
                scaler = 0.5 + 0.5 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"普攻倍率+{scaler}%生命上限",
                    target="NA",
                    multiplier=Multiplier(hp=scaler),
                )
            # 尘世之锁
            case "尘世之锁-金璋皇极":
                match setting.label.split("/"):
                    case n, s if n in ["1", "2", "3", "4", "5"] and s in ["0", "1"]:
                        stack, shield = int(n), int(s) + 1
                        setting.state = "{n}层，有护盾" if shield == 2 else "{n}层，无护盾"
                    case _:
                        setting.state, stack, shield = "×", 0, 0
                atk_per = (0.03 + 0.01 * weapon.affix_level) * stack * shield
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            # 四风原典
            case "四风原典-无边际的眷顾":
                match setting.label:
                    case x if x in ["1", "2", "3", "4"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "×", 0
                dmg_bonus = (0.06 + 0.02 * weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，元素增伤+{dmg_bonus:.0%}",
                    elem_dmg_bonus=DmgBonus().set("elem", dmg_bonus),
                )
            # ============================
            # ************四星*************
            # ============================
            # 流浪的晚星
            case "流浪的晚星-林野晚星":
                percent = 0.18 + 0.06 * weapon.affix_level
                atk = prop.elem_mastery * percent
                buff_info.buff = Buff(
                    dsc=f"基于精通的{percent:.0%}，攻击+({atk:.0f})",
                    atk=PoFValue(fix=atk),
                )
            case "流浪的晚星-林野晚星(队友)":
                percent = 0.18 + 0.06 * weapon.affix_level
                atk = prop.elem_mastery * percent * 0.3
                buff_info.buff = Buff(
                    dsc=f"队友攻击+{atk:.0f}",
                    atk=PoFValue(fix=atk),
                )
            case "盈满之实-圆满之相":
                match setting.label:
                    case x if x in ["1", "2", "3", "4", "5"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "×", 0
                elem_ma = (21 + 3 * weapon.affix_level) * stack
                atk_per = 0.05 * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}「盈缺」效果，精通+{elem_ma}，攻击-{atk_per:.0%}",
                    elem_mastery=elem_ma,
                    atk=PoFValue(percent=-atk_per),
                )
            case "证誓之明瞳-微光的海渊民":
                if setting.label == "-":
                    setting.state = "×"
                recharge = 0.18 + 0.06 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"施放元素战技10秒内，充能+{recharge:.0%}",
                    recharge=recharge,
                )
            case "白辰之环-樱之斋宫":
                elem_dmg_bonus = 0.075 + 0.025 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"触发雷元素相关反应6秒内，相应元素增伤+{elem_dmg_bonus:.0%}",
                )
                if (label in setting.label for label in ["火", "1"]):
                    setting.state += "火"
                    buff_info.buff.resist_reduction.set({"pyro": elem_dmg_bonus})
                if (label in setting.label for label in ["水", "2"]):
                    setting.state += "水"
                    buff_info.buff.resist_reduction.set({"hydro": elem_dmg_bonus})
                if (label in setting.label for label in ["冰", "3"]):
                    setting.state += "冰"
                    buff_info.buff.resist_reduction.set({"cryo": elem_dmg_bonus})
                if (label in setting.label for label in ["草", "4"]):
                    setting.state += "草"
                    buff_info.buff.resist_reduction.set({"dendro": elem_dmg_bonus})
                if (label in setting.label for label in ["风", "5"]):
                    setting.state += "风"
                    buff_info.buff.resist_reduction.set({"anemo": elem_dmg_bonus})
                if (label in setting.label for label in ["岩", "6"]):
                    setting.state += "岩"
                    buff_info.buff.resist_reduction.set({"geo": elem_dmg_bonus})
                if setting.state == "-":
                    setting.state = "×"
            case "嘟嘟可故事集-嘟嘟！大冒险(重击加成)":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.12 + 0.04 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"普攻命中6秒内，重击增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
            case "嘟嘟可故事集-嘟嘟！大冒险(攻击提升)":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.06 + 0.02 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"重击命中6秒内，攻击+{atk_per:.0%}(+{prop.atk_base*atk_per:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "暗巷的酒与诗-变化万端":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.15 + 0.05 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"使用冲刺或替代冲刺的能力5秒内，攻击+{atk_per:.0%}(+{prop.atk_base*atk_per:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "黑岩绯玉-乘胜追击":
                match setting.label:
                    case x if x in ["1", "2", "3"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "×", 0
                atk_per = (0.12 + 0.03 * weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，攻击+{atk_per:.0%}，持续30秒，每层独立",
                    atk=PoFValue(percent=atk_per),
                )
            case "万国诸海图谱-注能之卷":
                match setting.label:
                    case x if x in ["1", "2"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "×", 0
                dmg_bonus = (0.06 + 0.02 * weapon.affix_level) * stack
                buff_info.buff = Buff(
                    dsc=f"{setting.state}效果，元素增伤+{dmg_bonus:.0%}",
                    elem_dmg_bonus=DmgBonus().set({"elem": dmg_bonus}),
                )
            case "匣里日月-日月辉":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.15 + 0.05 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"普攻命中6秒内，元素战技与元素爆发增伤+{dmg_bonus:.0%}"
                    + f"元素战技与元素爆发命中6秒内，普攻增伤+{dmg_bonus:.0%}",
                    target=["NA", "E", "Q"],
                    dmg_bonus=dmg_bonus,
                )
            case "流浪乐章-登场乐":
                match setting.label:
                    case "1":
                        setting.state = "宣叙调"
                        atk_per = 0.45 + 0.15 * weapon.affix_level
                        buff_info.buff = Buff(
                            dsc=f"触发咏叹调，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                            atk=PoFValue(percent=atk_per),
                        )
                    case "2":
                        setting.state = "宣叙调"
                        dmg_bonus = 0.36 + 0.12 * weapon.affix_level
                        buff_info.buff = Buff(
                            dsc=f"触发咏叹调，元素增伤+{dmg_bonus:.0%}",
                            elem_dmg_bonus=DmgBonus().set({"elem": dmg_bonus}),
                        )
                    case "3":
                        setting.state = "间奏曲"
                        elem_ma = 180 + 60 * weapon.affix_level
                        buff_info.buff = Buff(
                            dsc=f"触发间奏曲，精通+{elem_ma}",
                            elem_mastery=elem_ma,
                        )
                    case _:
                        setting.state = "×"
            # ============================
            # ************三星*************
            # ============================
            case "甲级宝珏-奔袭战术":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.1 + 0.02 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"击杀15秒内，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "翡玉法球-激流":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.15 + 0.05 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"触发蒸发、感电、冰冻、绽放或水元素扩散12秒内，攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "讨龙英杰谭-传承":
                if setting.label == "-":
                    setting.state = "×"
                atk_per = 0.18 + 0.06 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"主动切换后，新登场角色攻击+{atk_per:.0%}(+{atk_per*prop.atk_base:.0f})，持续10秒",
                    atk=PoFValue(percent=atk_per),
                )
            case "魔导绪论-止水息雷":
                if setting.label == "-":
                    setting.state = "×"
                dmg_bonus = 0.09 + 0.03 * weapon.affix_level
                buff_info.buff = Buff(
                    dsc=f"敌方水或雷附着，增伤+{dmg_bonus:.0%}",
                    dmg_bonus=dmg_bonus,
                )
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
                        dsc="普攻叠层，①一半层数；②最大层数，提升普攻增伤",
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
                        dsc="同色元素队友的数量⓪~③，每名同色队友提升精通，每名异色队友提升元素增伤",
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
                        dsc="施放元素战技叠层，①~③每层提升元素战技增伤，满层提升额外元素增伤",
                        label=labels.get("神乐之真意-神乐舞", "3"),
                    ),
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="神乐之真意-神乐舞满层",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("神乐之真意-神乐舞满层", "○")),
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
                        dsc="攻击命中叠层，①~⑤每层提升攻击/⓪无护盾；①护盾下效果翻倍",
                        label=labels.get("尘世之锁-金璋皇极", "5/1"),
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
                        dsc="站场叠层，①~④每层提升元素增伤",
                        label=labels.get("四风原典-无边际的眷顾", "4"),
                    ),
                )
            )
        # ============================
        # ************四星*************
        # ============================
        case "流浪的晚星":
            output.append(
                BuffInfo(
                    source=source,
                    name="流浪的晚星-林野晚星",
                    buff_type="transbuff",
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="流浪的晚星-林野晚星(队友)",
                    buff_range="party",
                    buff_type="propbuff",
                )
            )
        case "盈满之实":
            output.append(
                BuffInfo(
                    source=source,
                    name="盈满之实-圆满之相",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="触发元素反应叠层，①~⑤每层提升精通，降低攻击",
                        label=labels.get("盈满之实-圆满之相", "5"),
                    ),
                )
            )

        case "白辰之环":
            output.append(
                BuffInfo(
                    source=source,
                    name="白辰之环-樱之斋宫",
                    buff_range="all",
                    setting=BuffSetting(
                        dsc="根据触发的雷相关反应，①火②水③冰④草⑤风⑥岩：同元素角色提升对应元素增伤",
                        label=labels.get("白辰之环-樱之斋宫", "火"),
                    ),
                )
            )
        case "嘟嘟可故事集":
            output.append(
                BuffInfo(
                    source=source,
                    name="嘟嘟可故事集-嘟嘟！大冒险(重击加成)",
                    setting=BuffSetting(label=labels.get("嘟嘟可故事集-嘟嘟！大冒险(重击加成)", "○")),
                )
            )
            output.append(
                BuffInfo(
                    source=source,
                    name="嘟嘟可故事集-嘟嘟！大冒险(攻击提升)",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("嘟嘟可故事集-嘟嘟！大冒险(攻击提升)", "○")),
                )
            )
        case "暗巷的酒与诗":
            output.append(
                BuffInfo(
                    source=source,
                    name="暗巷的酒与诗-变化万端",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("暗巷的酒与诗-变化万端", "○")),
                )
            )
        case "黑岩绯玉":
            output.append(
                BuffInfo(
                    source=source,
                    name="黑岩绯玉-乘胜追击",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="击杀叠层，①~③每层提升攻击，持续时间独立",
                        label=labels.get("黑岩绯玉-乘胜追击", "3"),
                    ),
                )
            )
        case "万国诸海图谱":
            output.append(
                BuffInfo(
                    source=source,
                    name="万国诸海图谱-注能之卷",
                    setting=BuffSetting(
                        dsc="触发元素反应叠层，①~②每层提升增伤，最大2层",
                        label=labels.get("万国诸海图谱-注能之卷", "2"),
                    ),
                )
            )
        case "匣里日月":
            output.append(
                BuffInfo(
                    source=source,
                    name="匣里日月-日月辉",
                    setting=BuffSetting(label=labels.get("匣里日月-日月辉", "○")),
                )
            )
        case "流浪乐章":
            output.append(
                BuffInfo(
                    source=source,
                    name="流浪乐章-登场乐",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="登场效果，①宣叙调：提升攻击；②咏叹调：提升元素增伤；③间奏曲：提升精通",
                        label=labels.get("流浪乐章-登场乐", "2"),
                    ),
                )
            )
        # ============================
        # ************三星*************
        # ============================
        case "甲级宝珏":
            output.append(
                BuffInfo(
                    source=source,
                    name="甲级宝珏-奔袭战术",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("甲级宝珏-奔袭战术", "○")),
                )
            )
        case "翡玉法球":
            output.append(
                BuffInfo(
                    source=source,
                    name="翡玉法球-激流",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("翡玉法球-激流", "○")),
                )
            )
        case "讨龙英杰谭":
            output.append(
                BuffInfo(
                    source=source,
                    name="讨龙英杰谭-传承",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("讨龙英杰谭-传承", "○")),
                )
            )
        case "魔导绪论":
            output.append(
                BuffInfo(
                    source=source,
                    name="魔导绪论-止水息雷",
                    setting=BuffSetting(label=labels.get("魔导绪论-止水息雷", "○")),
                )
            )
    return output

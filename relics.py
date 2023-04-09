from .classmodel import (
    Buff,
    BuffInfo,
    BuffSetting,
    DmgBonus,
    Info,
    Multiplier,
    PoFValue,
    ReaFactor,
)
from .dmg_calc import DmgCalc


def artifacts(buff_list: list[BuffInfo], info: Info, prop: DmgCalc):
    """
    提供圣遗物增益
    Args:
        buff_list:
        talent:
        prop:
    """

    for buff in buff_list:
        setting = buff.setting
        match buff.name:
            # =======五星========
            case "花神4":
                match setting.label:
                    case x if x in ["1", "2", "3", "4", "5"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "0层", 0
                factor = 0.4 + stack * 0.1
                buff.buff = Buff(
                    dsc=f"绽放系列反应系数+40%，触发绽放叠层，{stack}层额外反应系数+{stack*10}%",
                    reaction_coeff=ReaFactor(
                        bloom=factor, burgeon=factor, hyperbloom=factor
                    ),
                )
            case "沙阁4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="重击命中15秒内，攻速+10%，普攻、重击与下落增伤+40%",
                    target=["NA", "CA", "PA"],
                    dmg_bonus=0.4,
                )
            case "饰金4":
                match setting.label:
                    case x if x in ["0", "1", "2", "3"]:
                        setting.state, atk_per, em = (
                            f"{x}名异色",
                            0.14 * (3 - int(x)),
                            50 * int(x),
                        )
                    case _:
                        setting.state, atk_per, em = "×", 0, 0
                buff.buff = Buff(
                    dsc=f"触发元素反应8秒内，元素精通+{em}，攻击力+{atk_per:.0%}(+{prop.atk_base*atk_per:.0f})",
                    atk=PoFValue(percent=atk_per),
                    elem_mastery=em,
                )
            case "深林4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="元素战技或元素爆发命中8秒内，草抗-30%",
                    resist_reduction=DmgBonus(dendro=0.3),
                )
            case "青玉4-幽谷祝祀":
                buff.buff = Buff(
                    dsc="普攻倍率期望+35.14%",
                    target="NA",
                    mutiplier=Multiplier(atk=0.3514),
                )
            case "辰砂4-潜光":
                match setting.label:
                    case x if x in ["0", "1", "2", "3", "4"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "×", 0
                atk_per = 0.08 + stack * 0.1
                buff.buff = Buff(
                    dsc=f"施放元素爆发16秒内，{setting.state}层效果，攻击+{atk_per:.0%}(+{prop.atk_base*atk_per:.0f})",
                    atk=PoFValue(percent=atk_per),
                )
            case "华馆4-问答":
                match setting.label:
                    case x if x in ["1", "2", "3", "4"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "×", 0
                buff.buff = Buff(
                    dsc=f"岩元素命中{setting.state}，岩伤+{stack*6}%，防御+{stack*6}%(+{prop.def_base*stack*0.06:.0f})",
                    defense=PoFValue(percent=stack * 0.06),
                    elem_dmg_bonus=DmgBonus(geo=stack * 0.06),
                )
            case "绝缘4":
                dmg_bonus = min(prop.recharge * 0.25, 0.75)
                buff.buff = Buff(
                    dsc=f"基于充能，元素爆发增伤(+{dmg_bonus*100:.1f}%)，至多75%",
                    target="Q",
                    dmg_bonus=dmg_bonus,
                )
            case "追忆4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="施放元素战技10秒内，普攻、重击和下落增伤+50%",
                    target=["NA", "CA", "PA"],
                    dmg_bonus=0.5,
                )
            case "苍白4":
                match setting.label:
                    case "1":
                        setting.state = "1层"
                        buff.buff = Buff(
                            dsc=f"元素战技命中7秒内，攻击+9%(+{prop.atk_base * 0.09:.0f})",
                            atk=PoFValue(percent=0.09),
                        )
                    case "2":
                        setting.state = "2层"
                        buff.buff = Buff(
                            dsc=f"元素战技命中7秒内，攻击+18%(+{prop.atk_base * 0.18:.0f})，物伤+25%",
                            atk=PoFValue(percent=0.18),
                            elem_dmg_bonus=DmgBonus(phy=0.25),
                        )
                    case _:
                        setting.state = "×"
            case "千岩4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc=f"元素战技命中3秒内，全队护盾强效+30%且攻击+20%(+{prop.atk_base * 0.2:.0f})",
                    atk=PoFValue(percent=0.2),
                    shield_strength=0.3,
                )
            case "沉沦4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="施放元素战技15秒内，普攻和重击增伤+30%",
                    target=["NA", "CA"],
                    dmg_bonus=0.3,
                )
            case "流星4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="护盾庇护下，普攻和重击增伤+40%",
                    target=["NA", "CA"],
                    dmg_bonus=0.4,
                )

            case "磐岩4":
                buff.duration = 10
                buff.buff = Buff(dsc="获得结晶片10s内，对应元素增伤+35%")
                match setting.label:
                    case x if x in ["火", "1"]:
                        setting.state = "火"
                        buff.buff.elem_dmg_bonus = DmgBonus(pyro=0.35)
                    case x if x in ["水", "2"]:
                        setting.state = "水"
                        buff.buff.elem_dmg_bonus = DmgBonus(hydro=0.35)
                    case x if x in ["雷", "3"]:
                        setting.state = "雷"
                        buff.buff.elem_dmg_bonus = DmgBonus(electro=0.35)
                    case x if x in ["冰", "4"]:
                        setting.state = "冰"
                        buff.buff.elem_dmg_bonus = DmgBonus(cryo=0.35)
                    case _:
                        setting.state = "×"
            case "骑士4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="击败敌方10秒内，重击增伤+50%",
                    target="CA",
                    dmg_bonus=0.5,
                )
            case "宗室4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc=f"施放元素爆发12秒内，全队攻击+20%(+{prop.atk_base * 0.2:.0f})",
                    atk=PoFValue(percent=0.2),
                )
            case "宗室2":
                buff.buff = Buff(
                    target="Q",
                    dsc="元素爆发增伤+20％",
                    dmg_bonus=0.2,
                )
            case "魔女4-火伤":
                match setting.label:
                    case x if x in ["1", "2", "3"]:
                        setting.state, stack = f"{x}层", int(x)
                    case _:
                        setting.state, stack = "×", 0
                pyro_dmg = 0.075 * stack
                buff.buff = Buff(
                    dsc=f"施放元素战技10秒内，{setting.state}效果，火伤+{pyro_dmg:.0%}",
                    elem_dmg_bonus=DmgBonus(pyro=pyro_dmg),
                )
            case "魔女4-火反应":
                buff.buff = Buff(
                    dsc="超载、燃烧、烈绽放反应系数+40%，蒸发、融化反应系数+15%",
                    reaction_coeff=ReaFactor(
                        overloaded=0.4,
                        burning=0.4,
                        burgeon=0.4,
                        vaporize=0.15,
                        melt=0.15,
                    ),
                )
            case "如雷4":
                buff.buff = Buff(
                    dsc="超载、感电、超导、超绽放反应系数+40%，超激化反应系数+20%",
                    reaction_coeff=ReaFactor(
                        overloaded=0.4,
                        charged=0.4,
                        conduct=0.4,
                        hyperbloom=0.4,
                        aggravate=0.2,
                    ),
                )
            case "乐团4":
                if info.weapon_type in ["弓", "法器"]:
                    buff.buff = Buff(
                        dsc="弓，法器角色，重击增伤+35%",
                        target="CA",
                        dmg_bonus=0.35,
                    )
                else:
                    setting.state = "×"
            case "翠绿4-减抗":
                buff.duration = 10
                buff.buff = Buff(
                    dsc="触发扩散10s内，对应元素抗性-40%",
                )
                if (label in setting.label for label in ["火", "1"]):
                    setting.state += "火"
                    buff.buff.resist_reduction.set({"pyro": 0.4})
                if (label in setting.label for label in ["水", "2"]):
                    setting.state += "水"
                    buff.buff.resist_reduction.set({"hydro": 0.4})
                if (label in setting.label for label in ["雷", "3"]):
                    setting.state += "雷"
                    buff.buff.resist_reduction.set({"electro": 0.4})
                if (label in setting.label for label in ["冰", "4"]):
                    setting.state += "冰"
                    buff.buff.resist_reduction.set({"cryo": 0.4})
                if setting.state == "-":
                    setting.state = "×"
            case "翠绿4-扩散":
                buff.buff = Buff(
                    dsc="扩散反应系数+60%",
                    reaction_coeff=ReaFactor(swirl=0.6),
                )
            case "角斗4":
                if info.weapon_type in ["单手剑", "长柄武器", "双手剑"]:
                    buff.buff = Buff(
                        dsc="单手剑，长柄，双手剑角色，普攻增伤+35%",
                        target="NA",
                        dmg_bonus=0.35,
                    )
                else:
                    setting.state = "×"
            case "少女4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    target="H",
                    dsc="施放元素战技或元素爆发10秒内，全队受治疗+20%",
                    healing=0.2,
                )
            case "渡火4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="敌人火附着，增伤+35%",
                    dmg_bonus=0.35,
                )
            case "平雷4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="敌人雷附着，增伤+35%",
                    dmg_bonus=0.35,
                )

            case "冰风4":
                if setting.label in ["1", "冰附着"]:
                    setting.state = "冰附着"
                    buff.buff = Buff(
                        dsc="敌人冰附着，暴击+20%",
                        crit_rate=0.2,
                    )
                elif setting.label in ["2", "冻结"]:
                    setting.state = "冻结"
                    buff.buff = Buff(
                        dsc="敌人冻结，暴击+40%",
                        crit_rate=0.4,
                    )
                else:
                    setting.state = "×"
            # =======四星========
            case "战狂4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="角色生命<70%,暴击+24%",
                    crit_rate=0.24,
                )
            case "行者4":
                buff.buff = Buff(
                    dsc="重击暴击+30%",
                    target="CA",
                    crit_rate=0.3,
                )
            case "勇士4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="敌方生命>50%，增伤+30%",
                    dmg_bonus=0.3,
                )
            case "教官4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="触发反应8s内，精通+120",
                    elem_mastery=120,
                )

            case "赌徒2":
                buff.buff = Buff(
                    dsc="元素战技增伤+30%",
                    target="E",
                    dmg_bonus=0.3,
                )
            case "武人2":
                buff.buff = Buff(
                    dsc="普攻与重击增伤+15%",
                    target=["NA", "CA"],
                    dmg_bonus=0.15,
                )
            case "武人4":
                if setting.label == "-":
                    setting.state = "×"
                buff.buff = Buff(
                    dsc="施放元素战技8秒内，普攻与重击增伤+25%",
                    target=["NA", "CA"],
                    dmg_bonus=0.25,
                )


def artifacts_setting(
    suit: dict,
    labels: dict,
    role_name: str = "",
):
    """
    圣遗物增益设定
    """
    output: list[BuffInfo] = []

    source = f"{role_name}-圣遗物"
    for name, num in suit.items():
        match name:
            # =======五星========
            case "乐园遗落之花":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="花神4",
                            setting=BuffSetting(
                                dsc="触发绽放系列反应叠层，绽放系列初始反应系数+40%，①~④每层额外反应系数+10%",
                                label=labels.get("花神4", "4"),
                            ),
                        )
                    )
            case "沙上楼阁史话":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="沙阁4",
                            setting=BuffSetting(label=labels.get("沙阁4", "○")),
                        )
                    )
            case "饰金之梦":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="饰金4",
                            buff_type="propbuff",
                            setting=BuffSetting(
                                dsc="触发元素反应时，依据异色队友的元素，⓪~③每名异色精通+50，每名同色：攻击+14%",
                                label=labels.get("饰金4", "3"),
                            ),
                        )
                    )
            case "深林的记忆":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="深林4",
                            buff_range="all",
                            setting=BuffSetting(label=labels.get("深林4", "○")),
                        )
                    )
            case "来歆余响":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="青玉4-幽谷祝祀",
                        )
                    )
            case "辰砂往生录":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="辰砂4-潜光",
                            buff_type="propbuff",
                            setting=BuffSetting(
                                dsc="施放元素爆发后，降低生命叠层，初始攻击+8%，①~④每层额外攻击+10%",
                                label=labels.get("辰砂4-潜光", "4"),
                            ),
                        )
                    )
            case "华馆梦醒形骸记":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="华馆4-问答",
                            buff_type="propbuff",
                            setting=BuffSetting(
                                dsc="岩元素攻击命中叠层，①~④每层：防御+6%，岩伤+6%",
                                label=labels.get("华馆4-问答", "4"),
                            ),
                        )
                    )
            case "绝缘之旗印":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="绝缘4",
                        )
                    )
            case "追忆之注连":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="追忆4",
                            setting=BuffSetting(label=labels.get("追忆4", "○")),
                        )
                    )
            case "苍白之火":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="苍白4",
                            buff_type="propbuff",
                            setting=BuffSetting(
                                dsc="元素战技命中叠层，①~②每层攻击+9%，满层额外物伤+25%",
                                label=labels.get("苍白4", "2"),
                            ),
                        )
                    )
            case "千岩牢固":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="千岩4",
                            buff_range="all",
                            buff_type="propbuff",
                            setting=BuffSetting(label=labels.get("千岩4", "○")),
                        )
                    )
            case "沉沦之心":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="沉沦4",
                            setting=BuffSetting(label=labels.get("沉沦4", "○")),
                        )
                    )
            case "逆飞的流星":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="流星4",
                            setting=BuffSetting(label=labels.get("流星4", "○")),
                        )
                    )
            case "悠古的磐岩":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="磐岩4",
                            buff_range="all",
                            buff_type="propbuff",
                            setting=BuffSetting(
                                dsc="根据获取结晶片的元素，①火②水③雷④冰：全队对应元素增伤+35%",
                                label=labels.get("磐岩4", "火"),
                            ),
                        )
                    )
            case "染血的骑士道":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="骑士4",
                            setting=BuffSetting(label=labels.get("骑士4", "○")),
                        )
                    )
            case "昔日宗室之仪":
                if num >= 2:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="宗室2",
                        )
                    )
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="宗室4",
                            buff_range="all",
                            buff_type="propbuff",
                            setting=BuffSetting(label=labels.get("宗室4", "○")),
                        )
                    )
            case "炽烈的炎之魔女":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="魔女4-火反应",
                        )
                    )
                    output.append(
                        BuffInfo(
                            source=source,
                            name="魔女4-火伤",
                            buff_type="propbuff",
                            setting=BuffSetting(
                                dsc="施放元素战技叠层，①~③每层火伤+7.5%",
                                label=labels.get("魔女4-火伤", "3"),
                            ),
                        )
                    )
            case "如雷的盛怒":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="如雷4",
                        )
                    )
            case "流浪大地的乐团":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="乐团4",
                        )
                    )
            case "翠绿之影":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="翠绿4-扩散",
                        )
                    )
                    output.append(
                        BuffInfo(
                            source=source,
                            name="翠绿4-减抗",
                            buff_range="all",
                            setting=BuffSetting(
                                dsc="触发扩散（可重复），①火②水③雷④冰：对应抗性-40%",
                                label=labels.get("翠绿4-减抗", "火"),
                            ),
                        )
                    )
            case "角斗士的终幕礼":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="角斗4",
                        )
                    )
            case "被怜爱的少女":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="少女4",
                            setting=BuffSetting(label=labels.get("少女4", "○")),
                        )
                    )
            case "渡过烈火的贤人":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="渡火4",
                            setting=BuffSetting(label=labels.get("渡火4", "○")),
                        )
                    )
            case "平息鸣雷的尊者":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="平雷4",
                            setting=BuffSetting(label=labels.get("平雷4", "○")),
                        )
                    )
            case "冰风迷途的勇士":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="冰风4",
                            setting=BuffSetting(
                                dsc="敌方状态，①冰附着：暴击+20%；②冻结：暴击+40%",
                                label=labels.get("冰风4", "2"),
                            ),
                        )
                    )
            # =======四星========
            case "战狂":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="战狂4",
                            setting=BuffSetting(label=labels.get("战狂4", "○")),
                        )
                    )
            case "行者之心":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="行者4",
                        )
                    )
            case "勇士之心":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="勇士4",
                            setting=BuffSetting(label=labels.get("勇士4", "○")),
                        )
                    )
            case "教官":
                if num >= 4:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="教官4",
                            buff_range="all",
                            buff_type="propbuff",
                            setting=BuffSetting(label=labels.get("教官4", "○")),
                        )
                    )
            case "赌徒":
                if num >= 2:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="赌徒2",
                        )
                    )
            case "武人":
                if num >= 2:
                    output.append(
                        BuffInfo(
                            source=source,
                            name="武人2",
                        )
                    )
                    if num >= 4:
                        output.append(
                            BuffInfo(
                                source=source,
                                name="武人4",
                                setting=BuffSetting(label=labels.get("武人4", "○")),
                            )
                        )

    return output

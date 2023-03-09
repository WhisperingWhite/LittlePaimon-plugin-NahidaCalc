from .classmodel import Buff, BuffInfo, BuffSetting, DmgBonus, PoFValue
from .dmg_calc import DmgCalc


def resonance(buff_list: list[BuffInfo], prop: DmgCalc):
    """元素共鸣增益"""
    for buff_info in buff_list:
        setting = buff_info.setting
        match buff_info.name:
            case "热诚之火":
                buff_info.buff = Buff(
                    dsc=f"攻击力+25%(+{int(prop.atk_base*0.25)})",
                    atk=PoFValue(percent=0.25),
                )
            case "愈疗之水":
                buff_info.buff = Buff(
                    dsc=f"生命上限+25%(+{int(prop.hp_base*0.25)})",
                    hp=PoFValue(percent=0.25),
                )
            case "蔓生之草":
                buff_info.buff = Buff(
                    dsc="精通+50",
                    elem_mastery=50,
                )
                if setting.label == "1":
                    setting.state = "一级反应"
                    buff_info.buff.dsc += "；触发燃烧、原激化、绽放反应，额外精通+30"
                    buff_info.buff.elem_mastery += 30
                if setting.label == "2":
                    setting.state = "二级反应"
                    buff_info.buff.dsc += "；触发超/蔓激化、超/烈绽放，额外精通+20"
                    buff_info.buff.elem_mastery += 20
            case "粉碎之冰":
                buff_info.buff = Buff(
                    dsc="敌方冰元素影响下，暴击+15%",
                    crit_rate=0.15,
                )
            case "坚定之岩":
                buff_info.buff = Buff(
                    dsc="护盾强效+15%",
                    shield_strength=0.15,
                )
                if setting.label == "1":
                    setting.state = "护盾状态"
                    buff_info.buff.dsc += "，护盾下，增伤+15%，伤害命中，岩抗-20%"
                    buff_info.buff.dmg_bonus = 0.15
                    buff_info.buff.resist_reduction = DmgBonus(geo=0.2)


def resonance_setting(elements, settings: dict):
    """
    元素共鸣设置
    @params:
        elements: 共鸣元素 如： 水火
        settings: 标签设置
    """
    output: list[BuffInfo] = []
    source = "元素共鸣"
    for element in elements[0:2]:
        match element:
            case "火":
                output.append(
                    BuffInfo(
                        source=source,
                        name="热诚之火",
                        buff_type="propbuff",
                        setting=BuffSetting(),
                    )
                )
            case "水":
                output.append(
                    BuffInfo(
                        source=source,
                        name="愈疗之水",
                        buff_type="propbuff",
                        setting=BuffSetting(),
                    )
                )
            case "风":
                output.append(
                    BuffInfo(
                        source=source,
                        name="迅捷之风",
                        setting=BuffSetting(state="×"),
                    )
                )
            case "雷":
                output.append(
                    BuffInfo(
                        source=source,
                        name="强能之雷",
                        setting=BuffSetting(state="×"),
                    )
                )
            case "草":
                output.append(
                    BuffInfo(
                        source=source,
                        name="蔓生之草",
                        buff_type="propbuff",
                        setting=BuffSetting(
                            dsc="反应触发||⓪无：基础增益；①燃烧、原激化、绽放：精通+30；②超/蔓激化、超/烈绽放，精通+20",
                            label=settings.get("蔓生之草", "0"),
                        ),
                    )
                )
            case "冰":
                output.append(
                    BuffInfo(
                        source=source,
                        name="粉碎之冰",
                    )
                )
            case "岩":
                output.append(
                    BuffInfo(
                        source=source,
                        name="坚定之岩",
                        setting=BuffSetting(
                            dsc="护盾存在||⓪关（×）：基础增益；①存在：增伤+15%，岩抗-20%",
                            label=settings.get("坚定之岩", "1"),
                        ),
                    )
                )
    return output

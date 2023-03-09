from copy import deepcopy
from typing import Literal
from pathlib import Path
from numpy import argmin

from LittlePaimon.database import CharacterProperty
from LittlePaimon.utils.files import load_json

from .classmodel import BuffInfo, DmgBonus, FixValue, Multiplier, PoFValue, ReaFactor

ValueType = Literal["NA", "CA", "PA", "E", "Q", "H", "S", ""]
ElemType = Literal[
    "phy", "pyro", "electro", "hydro", "dendro", "anemo", "geo", "cryo", ""
]
DamageType = Literal["active", "off"]
ReaType = Literal[
    "蒸发",
    "融化",
    "蔓激化",
    "超激化",
    "燃烧",
    "超导",
    "扩散",
    "感电",
    "碎冰",
    "超载",
    "原绽放",
    "烈绽放",
    "超绽放",
    "结晶",
    "",
]

factor_map = load_json(path=Path(__file__).parent / "base_factor.json")


class DmgCalc:
    """
    伤害计算器
    """

    value_type: ValueType = ""
    """数值类型:NA-普攻 CA-重击 PA-下落攻击 E-战技 Q-爆发 H-治疗 S-护盾"""
    elem_type: ElemType = ""
    """伤害元素类型：\\
        phy-物理\\
        pyro-火属性\\
        electro-雷属性\\
        hydro-水属性\\
        dendro-草属性\\
        anemo-风属性\\
        geo-岩属性\\
        cryo-冰属性\\
    """
    damage_type: DamageType = "active"
    """出伤类型：
        active-驻场
        off-脱手
    """
    reaction_type: ReaType = ""
    """元素反应类型：\\
    剧变："燃烧", "超导", "扩散", "感电", "碎冰", "超载", "原绽放", "烈绽放", "超绽放", "结晶"\\
    增幅："蒸发", "融化", "蔓激化", "超激化"
    """
    multiplier: Multiplier = Multiplier()
    """倍率"""
    shield_strength: float = 0
    """护盾强效(他人)"""
    dmg_bonus: float = 0
    """增伤"""
    elem_resistance: DmgBonus = DmgBonus().set({"all": 0.1})
    """元素抗性"""
    def_resistance: float = 0
    """防御抗性"""
    def_piercing: float = 0
    """无视防御"""
    fix_value = FixValue()
    """固定伤害/治疗/盾量"""
    rea_factor: ReaFactor = ReaFactor().init()
    """反应系数加成"""

    def __init__(self, prop: CharacterProperty, level=90) -> None:
        self.level = level
        """等级"""
        self.hp = prop.health
        """生命上限"""
        self.atk = prop.attack
        """攻击力"""
        self.defense = prop.defense
        """防御力"""
        self.hp_base = prop.base_health
        """基础生命上限"""
        self.atk_base = prop.base_attack
        """基础攻击力"""
        self.def_base = prop.base_defense
        """基础防御力"""
        self.crit_rate = prop.crit_rate
        """暴击率"""
        self.crit_dmg = prop.crit_damage
        """暴击伤害"""
        self.elem_mastery = prop.elemental_mastery
        """元素精通"""
        self.recharge = prop.elemental_efficiency
        """充能"""
        self.elem_dmg_bonus = DmgBonus().set(prop.dmg_bonus)
        """各元素增伤"""
        self.healing = prop.healing_bonus
        """治疗"""

    def copy(self):
        return deepcopy(self)

    exlude_buffs: list[str] = []
    """去除的增益"""

    def set(
        self,
        value_type: ValueType = "",
        elem_type: ElemType = "",
        damage_type: DamageType = "active",
        reaction_type: ReaType = "",
        multiplier: Multiplier = Multiplier(),
        fix_value: FixValue = FixValue(),
        exlude_buffs: list[str] = [],
    ):
        """
        函数：设定伤害属性\\
        Params:
            value_type  :数值类型
            elem_type   :伤害元素类型
            damage_type :是否脱手
            reaction_type :反应类型
            multiplier   :倍率
            fix_value   :基础值
            exlude_buffs:无效增益
        """
        self.value_type = value_type
        self.elem_type = elem_type
        self.damage_type = damage_type
        self.reaction_type = reaction_type
        self.multiplier = multiplier
        self.fix_value = fix_value
        self.exlude_buffs = exlude_buffs
        return self

    def buff(
        self,
        extra_hp: PoFValue = PoFValue(),
        extra_atk: PoFValue = PoFValue(),
        extra_def: PoFValue = PoFValue(),
        extra_multiplier: Multiplier = Multiplier(),
        extra_crit_rate: float = 0,
        extra_crit_dmg: float = 0,
        extra_elem_mastery: float = 0,
        extra_recharge: float = 0,
        extra_elem_dmg_bonus: DmgBonus = DmgBonus(),
        extra_healing: float = 0,
        extra_shield: float = 0,
        extra_dmg_bonus: float = 0,
        resist_reduction: DmgBonus = DmgBonus(),
        def_reduction: float = 0,
        def_piercing: float = 0,
        extra_fixvalue: FixValue = FixValue(),
        extra_reaction_coeff: ReaFactor = ReaFactor(),
    ):
        """
        函数：获取增益后的面板数值
        @params: 面板增益数值
        @returns: 新面板数值
        """
        self.hp += extra_hp.fix + extra_hp.percent * self.hp_base
        self.atk += extra_atk.fix + extra_atk.percent * self.atk_base
        self.defense += extra_def.fix + extra_def.percent * self.def_base
        self.multiplier += extra_multiplier
        self.crit_rate += extra_crit_rate
        self.crit_dmg += extra_crit_dmg
        self.elem_mastery += extra_elem_mastery
        self.recharge += extra_recharge
        self.elem_dmg_bonus += extra_elem_dmg_bonus
        self.dmg_bonus += extra_dmg_bonus
        self.healing += extra_healing
        self.shield_strength += extra_shield
        self.elem_resistance -= resist_reduction
        self.def_resistance -= def_reduction
        self.def_piercing += def_piercing
        self.fix_value += extra_fixvalue
        self.rea_factor += extra_reaction_coeff
        return self

    @property
    def base_value(self):
        """基础数值"""
        return (
            self.multiplier.hp * self.hp
            + self.multiplier.atk * self.atk
            + self.multiplier.defense * self.defense
            + self.multiplier.em * self.elem_mastery
        ) / 100

    @property
    def base_dmg_zone(self):
        """基础伤害乘区"""
        return self.base_value + self.fix_value.dmg

    @property
    def dmg_bonus_zone(self):
        """增伤区"""
        return 1 + self.elem_dmg_bonus.get(self.elem_type) + self.dmg_bonus

    @property
    def expectation_hit_zone(self):
        """暴击期望区"""
        return 1 + min(max(self.crit_rate, 0), 1) * self.crit_dmg

    @property
    def crit_hit_zone(self):
        """必定暴击"""
        return 1 + self.crit_dmg

    @property
    def elem_res_zone(self):
        """抗性区"""
        if (elem_res := self.elem_resistance.get(self.elem_type)) < 0:
            return 1 - elem_res / 2
        elif elem_res <= 0.75:
            return 1 - elem_res
        else:
            return 1 / (1 + elem_res * 4)

    @property
    def def_res_zone(self):
        """防御区"""
        return (self.level + 100) / (
            (self.level + 100)
            + (1 - self.def_piercing) * (1 + self.def_resistance) * (90 + 100)
        )

    @property
    def reaction_zone(self):
        """反应区"""
        match self.reaction_type:
            case x if x in ["蒸发", "融化"]:
                em_factor = 2.78 * self.elem_mastery / (self.elem_mastery + 1400)
            case x if x in ["蔓激化", "超激化"]:
                em_factor = 5 * self.elem_mastery / (self.elem_mastery + 1200)
            case "结晶":
                em_factor = 4.44 * self.elem_mastery / (self.elem_mastery + 1400)
            case _:
                em_factor = 16 * self.elem_mastery / (self.elem_mastery + 2000)
        return self.rea_factor.get(self.reaction_type) + em_factor

    def get_pure_dmg(self, mode="") -> float:
        """
        非反应伤害计算器
        Params:
            mode:   "exp":期望伤害
                    "crit":暴击伤害
                    "":无暴击
        """
        if mode == "exp":
            crit_zone = self.expectation_hit_zone
        elif mode == "crit":
            crit_zone = self.crit_hit_zone
        else:
            crit_zone = 1

        return (
            self.base_dmg_zone
            * self.dmg_bonus_zone
            * self.elem_res_zone
            * self.def_res_zone
            * crit_zone
        )

    def get_amp_reac_dmg(self, mode=""):
        """
        增幅反应伤害
        Amplifying Reactions
        """
        match self.reaction_type:
            case x if x in ["蒸发", "融化"]:
                if (x == "蒸发" and self.elem_type == "pyro") or (
                    x == "融化" and self.elem_type == "cryo"
                ):
                    return 1.5 * self.reaction_zone * self.get_pure_dmg(mode)
                else:
                    return 2 * self.reaction_zone * self.get_pure_dmg(mode)
            case x if x in ["蔓激化"]:
                boost = factor_map["TransReac"][self.level] * 1.25 * self.reaction_zone
                return self.buff(extra_fixvalue=FixValue(dmg=boost)).get_pure_dmg(
                    mode=mode
                )
            case x if x in ["超激化"]:
                boost = factor_map["TransReac"][self.level] * 1.15 * self.reaction_zone
                return self.buff(extra_fixvalue=FixValue(dmg=boost)).get_pure_dmg(
                    mode=mode
                )
            case _:
                return self.get_pure_dmg(mode)

    def get_dmg(self):
        """直伤伤害"""
        return int(self.get_amp_reac_dmg("exp")), int(self.get_amp_reac_dmg("crit"))

    def get_trans_reac_dmg(self):
        """
        剧变反应伤害
        Transformative Reactions
        """
        factor_list = {
            "燃烧": 0.25,
            "超导": 0.5,
            "扩散": 0.6,
            "感电": 1.2,
            "碎冰": 1.5,
            "超载": 2,
            "原绽放": 2,
            "烈绽放": 3,
            "超绽放": 3,
        }
        if self.reaction_type in factor_list.keys():
            match self.reaction_type:
                case x if x in ["燃烧", "超载"]:
                    self.elem_type = "pyro"
                case "超导":
                    self.elem_type = "cryo"
                case "扩散":
                    match argmin(
                        [
                            self.elem_resistance.pyro,
                            self.elem_resistance.electro,
                            self.elem_resistance.hydro,
                            self.elem_resistance.cryo,
                        ]
                    ):
                        case 0:
                            self.elem_type = "pyro"
                        case 1:
                            self.elem_type = "electro"
                        case 2:
                            self.elem_type = "hydro"
                        case 3:
                            self.elem_type = "cryo"
                case "感电":
                    self.elem_type = "electro"
                case "碎冰":
                    self.elem_type = "phy"
                case x if x in ["原绽放", "烈绽放", "超绽放"]:
                    self.elem_type = "dendro"
            return (
                factor_list[self.reaction_type]
                * factor_map["TransReac"][self.level - 1]
                * self.reaction_zone
                * self.elem_res_zone
            )
        else:
            return 0

    def get_crystall_shield(self):
        """结晶盾"""
        if self.reaction_type == "结晶":
            return factor_map["Cryst"][self.level] * self.reaction_zone
        return 0

    def get_healing(self):
        """治疗量"""
        return (self.base_value + self.fix_value.heal) * (1 + self.healing)

    def get_shield(self):
        """盾量"""
        return (self.base_value + self.fix_value.shield) * (1 + self.shield_strength)

    def __add__(self, other: list[BuffInfo]):
        calc = self.copy()
        for buff_info in other:
            if buff_info.name in self.exlude_buffs:
                continue

            if buff_info.setting.state == "×":
                continue

            buff = buff_info.buff
            if all(e not in buff.target for e in ["ALL", calc.value_type]):
                continue

            if calc.damage_type == "off" and "active" == buff_info.buff_range:
                continue
            # if calc.member_type == "off" and "active" in buff.triger_type:
            #     continue

            calc.buff(
                extra_hp=buff.hp,
                extra_atk=buff.atk,
                extra_def=buff.defense,
                extra_multiplier=buff.multiplier,
                extra_crit_rate=buff.crit_rate,
                extra_crit_dmg=buff.crit_dmg,
                extra_elem_mastery=buff.elem_mastery,
                extra_recharge=buff.recharge,
                extra_elem_dmg_bonus=buff.elem_dmg_bonus,
                extra_dmg_bonus=buff.dmg_bonus,
                extra_healing=buff.healing,
                extra_shield=buff.shield_strength,
                resist_reduction=buff.resist_reduction,
                def_reduction=buff.def_reduction,
                def_piercing=buff.def_piercing,
                extra_fixvalue=buff.fix_value,
                extra_reaction_coeff=buff.reaction_coeff,
            )
        return calc

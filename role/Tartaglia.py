from ..classmodel import Dmg, BuffInfo, Multiplier
from ._model import Role


class Tartaglia(Role):
    name = "达达利亚"

    def skill_A(self, dmg_info: Dmg):
        """断流·破"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("普通攻击·断雨", self.talents[0].level, "断流·破 伤害").replace(
                "%", ""
            )
        )
        calc.set(
            value_type="NA",
            elem_type="hydro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_E1(self, dmg_info: Dmg):
        """魔王武装·狂澜-重击"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("魔王武装·狂澜", self.talents[1].level, "重击伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="hydro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_E2(self, dmg_info: Dmg):
        """断流·斩"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("魔王武装·狂澜", self.talents[1].level, "断流·斩伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="hydro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q1(self, dmg_info: Dmg, reaction=""):
        """尽灭水光"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("极恶技·尽灭闪", self.talents[2].level, "技能伤害·远程").replace(
                "%", ""
            )
        )
        calc.set(
            value_type="Q",
            elem_type="hydro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q2(self, dmg_info: Dmg):
        """断流·爆"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("极恶技·尽灭闪", self.talents[2].level, "断流·爆伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="hydro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    category: str = "站场主C"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["站场主C"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "站场主C":
                return ["攻击", "攻击%", "水伤", "暴击", "暴伤", "精通"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        return []

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""

    def weight(self, weights: dict, ex_buffs: dict):
        """伤害权重"""
        self.dmg_list = [
            Dmg(
                index=0,
                name="充能效率阈值",
                weight=weights.get("充能效率阈值", 100),
            ),
            Dmg(
                index=1,
                source="A",
                name="断流·破",
                dsc="断流·破伤害",
                weight=weights.get("断流·破", 0),
                exclude_buff=ex_buffs.get("断流·破", []),
            ),
            Dmg(
                index=2,
                source="E",
                name="魔王武装·狂澜-重击",
                dsc="魔王武装重击",
                weight=weights.get("魔王武装·狂澜-重击", 0),
                exclude_buff=ex_buffs.get("魔王武装·狂澜-重击", []),
            ),
            Dmg(
                index=3,
                source="E",
                name="断流·斩",
                dsc="断流·斩伤害",
                weight=weights.get("断流·斩", 0),
                exclude_buff=ex_buffs.get("断流·斩", []),
            ),
            Dmg(
                index=4,
                source="Q",
                name="尽灭水光-蒸发",
                dsc="Q近战",
                weight=weights.get("尽灭水光-蒸发", 0),
                exclude_buff=ex_buffs.get("尽灭水光-蒸发", []),
            ),
            Dmg(
                index=5,
                source="Q",
                name="断流·爆",
                dsc="断流·爆",
                weight=weights.get("断流·爆", 0),
                exclude_buff=ex_buffs.get("断流·爆", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "断流·破":
                        self.skill_A(dmg)
                    case "魔王武装·狂澜-重击":
                        self.skill_E1(dmg)
                    case "断流·斩":
                        self.skill_E2(dmg)
                    case "尽灭水光-蒸发":
                        self.skill_Q1(dmg, "蒸发")
                    case "断流·爆":
                        self.skill_Q2(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "站场主C":
                return {
                    "充能效率阈值": 120,
                    "断流·破": 10,
                    "魔王武装·狂澜-重击": 10,
                    "断流·斩": 10,
                    "尽灭水光-蒸发": 10,
                    "断流·爆": 10,
                }

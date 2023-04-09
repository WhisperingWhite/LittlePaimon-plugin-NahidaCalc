from ..classmodel import (
    Buff,
    BuffInfo,
    BuffSetting,
    Dmg,
    DmgBonus,
    FixValue,
    Multiplier,
)
from ._model import Role


class Qin(Role):
    name = "琴"

    def buff_C1(self, buff_info: BuffInfo):
        """流转剑脊的暴风"""
        buff_info.buff = Buff(
            dsc="风压剑长按1秒后，其增伤+40%",
            target="E",
            dmg_bonus=0.4,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """蒲公英的国土"""
        buff_info.buff = Buff(
            dsc="蒲公英之风领域内，风抗-40%",
            resist_reduction=DmgBonus(anemo=0.4),
        )

    def skill_E(self, dmg_info: Dmg):
        """风压剑"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("风压剑", self.talents[1].level, "技能伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="anemo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q_dmg(self, dmg_info: Dmg):
        """蒲公英之风"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("蒲公英之风", self.talents[2].level, "爆发伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="anemo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q_healing(self, dmg_info: Dmg):
        """蒲公英之风·蒲公英领域"""
        calc = self.create_calc()
        scaler, fix_value = [
            float(num)
            for num in self.get_scaler("蒲公英之风", self.talents[1].level, "领域发动治疗量")
            .replace("%攻击力", "")
            .split("+")
        ]
        calc.set(
            multiplier=Multiplier(atk=scaler),
            fix_value=FixValue(heal=fix_value),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value = calc.calc_dmg.get_healing()

    category: str = "副C"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["奶辅", "副C"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "奶辅":
                return ["攻击", "攻击%", "充能", "治疗"]
            case "副C":
                return ["攻击", "攻击%", "风伤", "暴击", "暴伤"]

    def setting(self, labels: dict) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []

        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="流转剑脊的暴风",
                    setting=BuffSetting(label=labels.get("流转剑脊的暴风", "○")),
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="蒲公英的国土",
                        buff_range="all",
                        setting=BuffSetting(label=labels.get("蒲公英的国土", "○")),
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "流转剑脊的暴风":
                    self.buff_C1(buff)
                case "蒲公英的国土":
                    self.buff_C4(buff)

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
                source="E",
                name="风压剑",
                dsc="E一段",
                weight=weights.get("风压剑", 0),
                exclude_buff=ex_buffs.get("风压剑", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="蒲公英之风",
                dsc="Q爆发",
                weight=weights.get("蒲公英之风", 0),
                exclude_buff=ex_buffs.get("蒲公英之风", []),
            ),
            Dmg(
                index=3,
                source="Q",
                name="蒲公英之风·蒲公英领域",
                value_type="H",
                dsc="Q治疗",
                weight=weights.get("蒲公英之风·蒲公英领域", 0),
                exclude_buff=ex_buffs.get("蒲公英之风·蒲公英领域", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "风压剑":
                        self.skill_E(dmg)
                    case "蒲公英之风":
                        self.skill_Q_dmg(dmg)
                    case "蒲公英之风·蒲公英领域":
                        self.skill_Q_healing(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "奶辅":
                return {
                    "充能效率阈值": 220,
                    "风压剑": 0,
                    "蒲公英之风": 0,
                    "蒲公英之风-蒲公英领域": 10,
                }
            case "副C":
                return {
                    "充能效率阈值": 180,
                    "风压剑": -1,
                    "蒲公英之风": 10,
                    "蒲公英之风-蒲公英领域": 2,
                }
            case _:
                return {
                    "充能效率阈值": 180,
                    "风压剑": 10,
                    "蒲公英之风": 10,
                    "蒲公英之风-蒲公英领域": 10,
                }

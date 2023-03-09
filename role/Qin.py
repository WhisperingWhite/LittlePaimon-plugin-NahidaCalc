from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, FixValue, Multiplier
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
        scaler, fix_value = float(
            self.get_scaler("蒲公英之风", self.talents[2].level, "领域发动治疗量")
            .replace("%攻击力", "")
            .split("+")
        )
        calc.set(
            multiplier=Multiplier(atk=scaler),
            fix_value=FixValue(heal=fix_value),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_healing())

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []

        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="流转剑脊的暴风",
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="蒲公英的国土",
                        buff_range="all",
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
                source="Q",
                name="蒲公英之风",
                dsc="Q爆发",
                weight=weights.get("蒲公英之风", 0),
                exclude_buff=ex_buffs.get("蒲公英之风", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="蒲公英之风-蒲公英领域",
                value_type="H",
                dsc="Q治疗",
                weight=weights.get("蒲公英之风-蒲公英领域", 0),
                exclude_buff=ex_buffs.get("蒲公英之风-蒲公英领域", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "蒲公英之风":
                        self.skill_Q_dmg(dmg)
                    case "蒲公英之风·蒲公英领域":
                        self.skill_Q_healing(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 200,
                    "蒲公英之风": -1,
                    "蒲公英之风-蒲公英领域": 10,
                }

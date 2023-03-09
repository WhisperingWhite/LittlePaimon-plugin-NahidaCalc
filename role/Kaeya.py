from ..classmodel import Dmg, Buff, BuffInfo, Multiplier
from ._model import Role


class Kaeya(Role):
    name = "凯亚"

    def buff_C1(self, buff_info: BuffInfo):
        """卓越的血脉"""
        buff_info.buff = Buff(
            dsc="敌方冰附着，普攻、重击暴击+15%",
            target=["NA", "CA"],
            crit_rate=0.15,
        )

    def skill_E(self, dmg_info: Dmg):
        """霜袭"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("霜袭", self.talents[1].level, "技能伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="cryo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

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
                    name="卓越的血脉",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "卓越的血脉":
                    self.buff_C1(buff)

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
                name="霜袭",
                dsc="E一段",
                weight=weights.get("霜袭", 0),
                exclude_buff=ex_buffs.get("霜袭", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "霜袭":
                        self.skill_E(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 160,
                    "霜袭": 10,
                }

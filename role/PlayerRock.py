from ..classmodel import Buff, BuffInfo, Dmg, Multiplier
from ._model import Role


class PlayerRock(Role):
    name = "岩主"

    def buff_C2(self, buff_info: BuffInfo):
        """巍然的青岩"""
        buff_info.buff = Buff(
            dsc="岩嶂包围中时，暴击+10%",
            crit_rate=0.1,
        )

    def skill_E(self, dmg_info: Dmg):
        """星陨剑"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("星陨剑", self.talents[1].level, "技能伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="geo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q(self, dmg_info: Dmg):
        """岩潮叠嶂"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("岩潮叠嶂", self.talents[2].level, "地震波单次伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="geo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="巍然的青岩",
                    buff_range="all",
                    buff_type="propbuff",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "巍然的青岩":
                    self.buff_C2(buff)

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
                name="星陨剑",
                dsc="E荒星单段",
                weight=weights.get("星陨剑", 0),
                exclude_buff=ex_buffs.get("星陨剑", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="岩潮叠嶂",
                dsc="Q地震波单段",
                weight=weights.get("岩潮叠嶂", 0),
                exclude_buff=ex_buffs.get("岩潮叠嶂", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "星陨剑":
                        self.skill_E(dmg)
                    case "岩潮叠嶂":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "星陨剑": 10,
                    "岩潮叠嶂": 10,
                }

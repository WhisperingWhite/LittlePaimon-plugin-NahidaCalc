from ..classmodel import Buff, BuffInfo, Dmg, Multiplier
from ._model import Role


class Heizo(Role):
    name = "平藏"

    def buff_T2(self, buff_info: BuffInfo):
        """因由勘破"""
        buff_info.buff = Buff(
            dsc="勠心拳命中10秒内，队友精通+80",
            elem_mastery=80,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """奇想天开捕物帐"""
        buff_info.buff = Buff(
            dsc="正论状态下施放勠心拳时，暴击+16%，暴伤+32%",
            crit_rate=0.16,
            crit_dmg=0.32,
        )

    def skill_E(self, dmg_info: Dmg):
        """勠心拳"""
        calc = self.create_calc()
        scaler0 = float(
            self.get_scaler("勠心拳", self.talents[1].level, "技能伤害").replace("%", "")
        )
        scaler1 = float(
            self.get_scaler("勠心拳", self.talents[1].level, "变格伤害提升").replace("%/层", "")
        )
        scaler2 = float(
            self.get_scaler("勠心拳", self.talents[1].level, "正论伤害提升").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="anemo",
            multiplier=Multiplier(atk=scaler0 + scaler1 * 4 + scaler2),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q(self, dmg_info: Dmg):
        """聚风蹴"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("聚风蹴", self.talents[2].level, "不动流·真空弹伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="anemo",
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
        # 天赋
        if self.info.ascension >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T2",
                    name="因由勘破",
                    buff_type="propbuff",
                )
            )
        # 命座
        if self.info.constellation >= 6:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C6",
                    name="奇想天开捕物帐",
                )
            )

        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "因由勘破":
                    self.buff_T2(buff)
                case "奇想天开捕物帐":
                    self.buff_C6(buff)

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
                name="勠心拳",
                dsc="Q正论勠心拳",
                weight=weights.get("勠心拳", 0),
                exclude_buff=ex_buffs.get("勠心拳", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="聚风蹴",
                dsc="Q不动流·真空弹",
                weight=weights.get("聚风蹴", 0),
                exclude_buff=ex_buffs.get("聚风蹴", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "勠心拳":
                        self.skill_E(dmg)
                    case "聚风蹴":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "勠心拳": 10,
                    "聚风蹴": 10,
                }

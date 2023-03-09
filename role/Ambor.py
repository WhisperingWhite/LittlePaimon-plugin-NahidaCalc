from ..classmodel import Dmg, Buff, BuffInfo, Multiplier, PoFValue
from ._model import Role


class Ambor(Role):
    name = "安柏"

    def buff_T1(self, buff_info: BuffInfo):
        """百发百中!"""
        buff_info.buff = Buff(
            dsc="箭雨暴击+10%",
            target="Q",
            crit_rate=0.1,
        )

    def buff_T2(self, buff_info: BuffInfo):
        """压制射击"""
        buff_info.buff = Buff(
            dsc=f"重击命中弱点10秒内,攻击+15%(+{0.15*self.prop.atk_base})",
            atk=PoFValue(percent=0.15),
        )

    def buff_C6(self, buff_info: BuffInfo):
        """疾如野火"""
        buff_info.buff = Buff(
            dsc=f"使用箭雨10秒内,全队攻击+15%(+{0.15*self.prop.atk_base})",
            atk=PoFValue(percent=0.15),
        )

    def skill_Q(self, dmg_info: Dmg):
        """箭雨"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("箭雨", self.talents[2].level, "箭雨单次伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="pyro",
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
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="百发百中!",
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="压制射击",
                        buff_type="propbuff",
                    )
                )
        # 命座
        if self.info.constellation >= 6:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C6",
                    name="疾如野火",
                    buff_range="all",
                    buff_type="propbuff",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "百发百中!":
                    self.buff_T1(buff)
                case "压制射击":
                    self.buff_T2(buff)
                case "疾如野火":
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
                source="Q",
                name="箭雨",
                dsc="Q箭雨单次",
                weight=weights.get("箭雨", 0),
                exclude_buff=ex_buffs.get("箭雨", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "箭雨":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 150,
                    "箭雨": 10,
                }

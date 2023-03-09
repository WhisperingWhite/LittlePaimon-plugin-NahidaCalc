from ..classmodel import Buff, BuffInfo, Dmg, Multiplier
from ._model import Role


class Collei(Role):
    name = "柯莱"

    def buff_C1(self, buff_info: BuffInfo):
        """巡护深林"""
        buff_info.buff = Buff(
            dsc="处于队伍后台时，充能+20%",
            recharge=0.2,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """骞林馈遗"""
        buff_info.buff = Buff(
            dsc="施放猫猫秘宝12秒内，队友精通+60",
            elem_mastery=60,
        )

    def skill_Q(self, dmg_info: Dmg):
        """猫猫秘宝"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("共相·理式摹写", self.talents[2].level, "爆发伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="dendro",
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
        if self.info.ascension >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="巡护深林",
                    buff_type="propbuff",
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="骞林馈遗",
                        buff_range="party",
                        buff_type="propbuff",
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "巡护深林":
                    self.buff_C1(buff)
                case "骞林馈遗":
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
                name="猫猫秘宝",
                dsc="Q首段爆发",
                weight=weights.get("猫猫秘宝", 0),
                exclude_buff=ex_buffs.get("猫猫秘宝", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "猫猫秘宝":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 180,
                    "猫猫秘宝": 10,
                }

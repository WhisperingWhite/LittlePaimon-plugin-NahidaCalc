from ..classmodel import Dmg, Buff, BuffInfo, DmgBonus, Multiplier
from ._model import Role


class Ayaka(Role):
    name = "绫华"

    def buff_T1(self, buff_info: BuffInfo):
        """天罪国罪镇词"""
        buff_info.buff = Buff(
            dsc="施放神里流·冰华6秒内，普攻、重击增伤+30%",
            target=["NA", "CA"],
            dmg_bonus=0.3,
        )

    def buff_T2(self, buff_info: BuffInfo):
        """寒天宣命祝词"""
        buff_info.buff = Buff(
            dsc="神里流·霰步命中10秒内，冰伤+18%",
            elem_dmg_bonus=DmgBonus(cryo=0.18),
        )

    def buff_C4(self, buff_info: BuffInfo):
        """盈缺流返"""
        buff_info.buff = Buff(
            dsc="雪关扉命中6秒内，减防+30%",
            def_reduction=0.3,
        )

    def skill_Q(self, dmg_info: Dmg):
        """神里流·霜灭"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("神里流·霜灭", self.talents[2].level, "切割伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
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
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="天罪国罪镇词",
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="寒天宣命祝词",
                        buff_type="propbuff",
                    )
                )
        # 命座
        if self.info.constellation >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C4",
                    name="盈缺流返",
                    buff_range="all",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "天罪国罪镇词":
                    self.buff_T1(buff)
                case "寒天宣命祝词":
                    self.buff_T2(buff)
                case "盈缺流返":
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
                name="神里流·霜灭",
                dsc="Q切割每段",
                weight=weights.get("神里流·霜灭", 0),
                exclude_buff=ex_buffs.get("神里流·霜灭", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "神里流·霜灭":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "神里流·霜灭": 10,
                }

from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, DmgBonus, Multiplier
from ._model import Role


class Ayaka(Role):
    name = "绫华"

    def buff_T1(self, buff_info: BuffInfo):
        """天罪国罪镇词"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="施放神里流·冰华6秒内，普攻、重击增伤+30%",
            target=["NA", "CA"],
            dmg_bonus=0.3,
        )

    def buff_T2(self, buff_info: BuffInfo):
        """寒天宣命祝词"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="神里流·霰步命中10秒内，冰伤+18%",
            elem_dmg_bonus=DmgBonus(cryo=0.18),
        )

    def buff_C4(self, buff_info: BuffInfo):
        """盈缺流返"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="雪关扉命中6秒内，减防+30%",
            def_reduction=0.3,
        )

    def skill_A(self, dmg_info: Dmg):
        """神里流·倾"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("普通攻击·神里流·倾", self.talents[0].level, "重击伤害").replace(
                "%*3", ""
            )
        )
        calc.set(
            value_type="CA",
            elem_type="cryo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_E(self, dmg_info: Dmg):
        """神里流·冰华"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("神里流·冰华", self.talents[1].level, "技能伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="cryo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

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

    category: str = "冻结主C"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["冻结主C", "副C"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case x if x in ["冻结主C", "副C"]:
                return ["攻击", "攻击%", "冰伤", "暴击", "暴伤"]
            case _:
                return ["攻击", "攻击%", "冰伤", "暴击", "暴伤"]

    def setting(self, labels: dict) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="天罪国罪镇词",
                    setting=BuffSetting(label=labels.get("天罪国罪镇词", "○")),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="寒天宣命祝词",
                        buff_type="propbuff",
                        setting=BuffSetting(label=labels.get("寒天宣命祝词", "○")),
                    )
                )
        # 命座
        if self.info.constellation >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C4",
                    name="盈缺流返",
                    buff_range="all",
                    setting=BuffSetting(label=labels.get("盈缺流返", "○")),
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
                source="A",
                name="神里流·倾",
                dsc="重击每段",
                weight=weights.get("神里流·倾", 0),
                exclude_buff=ex_buffs.get("神里流·倾", []),
            ),
            Dmg(
                index=2,
                source="E",
                name="神里流·冰华",
                dsc="E一段",
                weight=weights.get("神里流·冰华", 0),
                exclude_buff=ex_buffs.get("神里流·冰华", []),
            ),
            Dmg(
                index=3,
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
                    case "神里流·倾":
                        self.skill_A(dmg)
                    case "神里流·冰华":
                        self.skill_E(dmg)
                    case "神里流·霜灭":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case "冻结主C":
                return {
                    "充能效率阈值": 100,
                    "神里流·倾": -1,
                    "神里流·冰华": -1,
                    "神里流·霜灭": 10,
                }
            case "副C":
                return {
                    "充能效率阈值": 160,
                    "神里流·倾": 0,
                    "神里流·冰华": 0,
                    "神里流·霜灭": 10,
                }
            case _:
                return {
                    "充能效率阈值": 120,
                    "神里流·倾": -1,
                    "神里流·冰华": -1,
                    "神里流·霜灭": 10,
                }

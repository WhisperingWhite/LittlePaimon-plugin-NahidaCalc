from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, DmgBonus, Multiplier
from ._model import Role


class Ganyu(Role):
    name = "甘雨"

    def buff_T1(self, buff_info: BuffInfo):
        """唯此一心"""
        buff_info.buff = Buff(
            dsc="霜华矢发射5秒内，霜华矢和霜华绽发暴击+20%",
            target="CA",
            crit_rate=0.2,
        )

    def buff_T2(self, buff_info: BuffInfo):
        """天地交泰"""
        buff_info.buff = Buff(
            dsc="降众天华领域内,场上角色冰伤+20%",
            elem_dmg_bonus=DmgBonus(cryo=0.2),
        )

    def buff_C1(self, buff_info: BuffInfo):
        """饮露"""
        buff_info.buff = Buff(
            dsc="霜华矢命中6秒内，冰抗-15%",
            resist_reduction=DmgBonus(cryo=0.15),
        )

    def buff_C4(self, buff_info: BuffInfo):
        """西狩"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4", "5"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"降众天华领域内，对敌增伤+{5*s}%，持续3s",
            dmg_bonus=0.05 * s,
        )

    def skill_A(self, dmg_info: Dmg, reaction=""):
        """流天射术·霜华矢"""
        calc = self.create_calc()
        scaler = sum(
            [
                float(i.replace("%", ""))
                for i in self.get_scaler(
                    "普通攻击·流天射术",
                    self.talents[0].level,
                    "霜华矢命中伤害",
                    "霜华矢·霜华绽发伤害",
                )
            ]
        )
        calc.set(
            value_type="CA",
            elem_type="cryo",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q(self, dmg_info: Dmg):
        """降众天华"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("降众天华", self.talents[2].level, "冰棱伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="cryo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    category: str = ""
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["融甘", "冻甘"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "融甘":
                return ["攻击", "攻击%", "冰伤", "暴击", "暴伤", "精通"]
            case "冻甘":
                return ["攻击", "攻击%", "冰伤", "暴击", "暴伤"]
            case _:
                return ["攻击", "攻击%", "冰伤", "暴击", "暴伤"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="唯此一心",
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="天地交泰",
                        buff_range="active",
                        buff_type="propbuff",
                    )
                )
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="饮露",
                    buff_range="all",
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="西狩",
                        buff_range="active",
                        setting=BuffSetting(
                            dsc="降众天华领域内，随时间叠层，⓪~⑤每层：增伤+5%",
                            label=labels.get("西狩", "3"),
                        ),
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "唯此一心":
                    self.buff_T1(buff)
                case "天地交泰":
                    self.buff_T2(buff)
                case "饮露":
                    self.buff_C1(buff)
                case "西狩":
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
                name="流天射术·霜华矢",
                dsc="A二段蓄力",
                weight=weights.get("流天射术·霜华矢", 0),
                exclude_buff=ex_buffs.get("流天射术·霜华矢", []),
            ),
            Dmg(
                index=2,
                source="A",
                name="流天射术·霜华矢-融化",
                dsc="A二段蓄力融化",
                weight=weights.get("流天射术·霜华矢-融化", 0),
                exclude_buff=ex_buffs.get("流天射术·霜华矢-融化", []),
            ),
            Dmg(
                index=3,
                source="Q",
                name="降众天华",
                dsc="冰棱每段",
                weight=weights.get("降众天华", 0),
                exclude_buff=ex_buffs.get("降众天华", ["天地交泰", "西狩"]),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "流天射术·霜华矢":
                        self.skill_A(dmg)
                    case "流天射术·霜华矢-融化":
                        self.skill_A(dmg, "融化")
                    case "降众天华":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "融甘":
                return {
                    "充能效率阈值": 100,
                    "流天射术·霜华矢": 0,
                    "流天射术·霜华矢-融化": 10,
                    "降众天华": -1,
                }
            case "冻甘":
                return {
                    "充能效率阈值": 110,
                    "流天射术·霜华矢": 5,
                    "流天射术·霜华矢-融化": 0,
                    "降众天华": 10,
                }
            case _:
                return {
                    "充能效率阈值": 100,
                    "流天射术·霜华矢": 5,
                    "流天射术·霜华矢-融化": -1,
                    "降众天华": 10,
                }

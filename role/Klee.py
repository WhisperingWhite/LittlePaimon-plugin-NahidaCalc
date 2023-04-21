from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, DmgBonus, Multiplier
from ._model import Role


class Klee(Role):
    name = "可莉"

    def buff_T1(self, buff_info: BuffInfo):
        """砰砰礼物"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="拥有爆裂火花时，重击增伤+50%",
            target="CA",
            dmg_bonus=0.5,
        )

    def buff_C2(self, buff_info: BuffInfo):
        """破破弹片"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="诡雷命中10秒内，减防+23%",
            def_reduction=0.23,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """火力全开"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="施放轰轰火花25秒内，所有角色火伤+10%",
            elem_dmg_bonus=DmgBonus(pyro=0.1),
        )

    def skill_A(self, dmg_info: Dmg, reaction=""):
        """砰砰"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("普通攻击·砰砰", self.talents[0].level, "重击伤害").replace("%", "")
        )
        calc.set(
            value_type="CA",
            elem_type="pyro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_E(self, dmg_info: Dmg):
        """蹦蹦炸弹"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("蹦蹦炸弹", self.talents[1].level, "蹦蹦炸弹伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="pyro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q(self, dmg_info: Dmg):
        """轰轰火花"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("轰轰火花", self.talents[2].level, "轰轰火花伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="pyro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    category: str = "纯火可莉"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["纯火可莉", "蒸可"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "纯火可莉":
                return ["攻击", "攻击%", "火伤", "暴击", "暴伤"]
            case "蒸可":
                return ["攻击", "攻击%", "火伤", "暴击", "暴伤", "精通"]

    def setting(self, labels: dict) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="砰砰礼物",
                    setting=BuffSetting(label=labels.get("砰砰礼物", "○")),
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="破破弹片",
                    buff_range="all",
                    setting=BuffSetting(label=labels.get("破破弹片", "○")),
                )
            )
            if self.info.constellation >= 6:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C6",
                        name="火力全开",
                        buff_range="all",
                        buff_type="propbuff",
                        setting=BuffSetting(label=labels.get("火力全开", "○")),
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "砰砰礼物":
                    self.buff_T1(buff)
                case "破破弹片":
                    self.buff_C2(buff)
                case "火力全开":
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
                source="A",
                name="砰砰",
                dsc="A重击",
                weight=weights.get("砰砰", 0),
                exclude_buff=ex_buffs.get("砰砰", []),
            ),
            Dmg(
                index=2,
                source="A",
                name="砰砰-蒸发",
                dsc="A重击蒸发",
                weight=weights.get("砰砰-蒸发", 0),
                exclude_buff=ex_buffs.get("砰砰-蒸发", []),
            ),
            Dmg(
                index=3,
                source="E",
                name="蹦蹦炸弹",
                dsc="E蹦蹦",
                weight=weights.get("蹦蹦炸弹", 0),
                exclude_buff=ex_buffs.get("蹦蹦炸弹", []),
            ),
            Dmg(
                index=4,
                source="Q",
                name="轰轰火花",
                dsc="Q火花每段",
                weight=weights.get("轰轰火花", 0),
                exclude_buff=ex_buffs.get("轰轰火花", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "砰砰":
                        self.skill_A(dmg)
                    case "砰砰-蒸发":
                        self.skill_A(dmg, "蒸发")
                    case "蹦蹦炸弹":
                        self.skill_E(dmg)
                    case "轰轰火花":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "纯火可莉":
                return {
                    "充能效率阈值": 100,
                    "砰砰": 10,
                    "砰砰-蒸发": 0,
                    "蹦蹦炸弹": 10,
                    "轰轰火花": 10,
                }
            case "蒸可":
                return {
                    "充能效率阈值": 100,
                    "砰砰": 0,
                    "砰砰-蒸发": 10,
                    "蹦蹦炸弹": 0,
                    "轰轰火花": 0,
                }
            case _:
                return {
                    "充能效率阈值": 100,
                    "砰砰": -1,
                    "砰砰-蒸发": 10,
                    "蹦蹦炸弹": -1,
                    "轰轰火花": -1,
                }

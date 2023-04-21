from ..classmodel import (
    Dmg,
    Buff,
    BuffInfo,
    BuffSetting,
    DmgBonus,
    Multiplier,
    PoFValue,
)
from ._model import Role


class Yoimiya(Role):
    name = "宵宫"

    def buff_T1(self, buff_info: BuffInfo):
        """袖火百景图"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"焰硝庭火舞持续期间，普攻命中叠层，火伤+{2*s}%",
            elem_dmg_bonus=DmgBonus(pyro=0.02 * s),
        )

    def buff_T2(self, buff_info: BuffInfo):
        """炎昼风物诗"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        atk_per = 0.1 + 0.01 * s
        buff_info.buff = Buff(
            dsc="释放琉金云间草15秒内，攻击+10%，"
            + f"依据袖火百景图层数，额外攻击+{s}%(共+{atk_per*self.prop.atk_base})",
            atk=PoFValue(percent=atk_per),
        )

    def buff_C1(self, buff_info: BuffInfo):
        """赤玉琉金"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="击败琉金火光影响下的敌方15秒内，攻击力+20%",
            atk=PoFValue(percent=0.2),
        )

    def buff_C2(self, buff_info: BuffInfo):
        """万灯送火"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="火元素伤害暴击6秒内，火伤+25%",
            elem_dmg_bonus=DmgBonus(pyro=0.25),
        )

    def skill_A(self, dmg_info: Dmg, reaction=""):
        """烟火打扬"""
        calc = self.create_calc()
        scaler1, scaler2, scaler3, scaler4, scaler5 = [
            float(num.replace("%", "").replace("*2", ""))
            for num in self.get_scaler(
                "普通攻击·烟火打扬",
                self.talents[0].level,
                "一段伤害",
                "二段伤害",
                "三段伤害",
                "四段伤害",
                "五段伤害",
            )
        ]
        scaler_rea = scaler1 + scaler3 + scaler5
        scaler = scaler1 + scaler2 + scaler4 * 2
        calc.set(
            value_type="NA",
            elem_type="pyro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler_rea * self.E_mul),
            exlude_buffs=dmg_info.exclude_buff,
        )
        exp_value1, crit_value1 = calc.calc_dmg.get_dmg()

        calc.set(
            value_type="NA",
            elem_type="pyro",
            multiplier=Multiplier(atk=scaler * self.E_mul),
            exlude_buffs=dmg_info.exclude_buff,
        )
        exp_value2, crit_value2 = calc.calc_dmg.get_dmg()
        dmg_info.exp_value, dmg_info.crit_value = (
            exp_value1 + exp_value2,
            crit_value1 + crit_value2,
        )

    E_mul: float = 1
    """焰硝庭火舞对普攻倍率乘数"""

    def buff_E(self, buff_info: BuffInfo):
        """焰硝庭火舞"""
        self.E_mul = (
            float(
                self.get_scaler("焰硝庭火舞", self.talents[1].level, "炽焰箭伤害").replace(
                    "%普通攻击伤害", ""
                )
            )
            / 100
        )
        buff_info.buff = Buff(
            dsc=f"施放焰硝庭火舞，普攻倍率×{self.E_mul:1%}",
        )

    category: str = "蒸宵"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["蒸宵", "纯火宵"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "蒸宵":
                return ["攻击", "攻击%", "火伤", "暴击", "暴伤", "精通"]
            case "纯火宵":
                return ["攻击", "攻击%", "火伤", "暴击", "暴伤"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="袖火百景图",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="焰硝庭火舞时，普攻命中叠层，⓪~⑩每层：火伤+2%",
                        label=labels.get("袖火百景图", "10"),
                    ),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="炎昼风物诗",
                        buff_range="party",
                        buff_type="propbuff",
                        setting=BuffSetting(
                            dsc="释放琉金云间草，依据袖火百景图层数，⓪~⑩每层：攻击+1%",
                            label=labels.get("炎昼风物诗", "1"),
                        ),
                    )
                )
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="赤玉琉金",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("赤玉琉金", "○")),
                )
            )
            if self.info.constellation >= 2:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C2",
                        name="万灯送火",
                        buff_type="propbuff",
                        setting=BuffSetting(label=labels.get("万灯送火", "○")),
                    )
                )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="焰硝庭火舞",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "袖火百景图":
                    self.buff_T1(buff)
                case "炎昼风物诗":
                    self.buff_T2(buff)
                case "赤玉琉金":
                    self.buff_C1(buff)
                case "万灯送火":
                    self.buff_C2(buff)
                case "焰硝庭火舞":
                    self.buff_E(buff)

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
                name="烟火打扬",
                dsc="A一轮五段",
                weight=weights.get("烟火打扬", 0),
                exclude_buff=ex_buffs.get("烟火打扬", []),
            ),
            Dmg(
                index=1,
                source="A",
                name="烟火打扬-蒸发",
                dsc="A一轮五段蒸发",
                weight=weights.get("烟火打扬-蒸发", 0),
                exclude_buff=ex_buffs.get("烟火打扬-蒸发", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "烟火打扬":
                        self.skill_A(dmg, "")
                    case "烟火打扬-蒸发":
                        self.skill_A(dmg, "蒸发")
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "蒸宵":
                return {
                    "充能效率阈值": 100,
                    "烟火打扬": 0,
                    "烟火打扬-蒸发": 10,
                }
            case "纯火宵":
                return {
                    "充能效率阈值": 100,
                    "烟火打扬": 10,
                    "烟火打扬-蒸发": 0,
                }
            case _:
                return {
                    "充能效率阈值": 100,
                    "烟火打扬": -1,
                    "烟火打扬-蒸发": 10,
                }

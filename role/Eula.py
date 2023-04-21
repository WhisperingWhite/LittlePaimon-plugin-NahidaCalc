from ..classmodel import (
    Buff,
    BuffInfo,
    BuffSetting,
    Dmg,
    DmgBonus,
    Multiplier,
    PoFValue,
)
from ._model import Role


class Eula(Role):
    name = "优菈"

    def buff_C1(self, buff_info: BuffInfo):
        """光潮的幻象"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="消耗冷酷之心，物伤+30%，持续6秒可延长",
            elem_dmg_bonus=DmgBonus(phy=0.3),
        )

    def buff_C4(self, buff_info: BuffInfo):
        """自卑者的逞强"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="对生命低于50%的敌人，光降之剑增伤+25%",
            target="Q",
            dmg_bonus=0.25,
        )

    def skill_A(self, dmg_info: Dmg):
        """西风剑术·宗室"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("普通攻击·西风剑术·宗室", self.talents[0].level, "一段伤害").replace(
                "%", ""
            )
        )
        calc.set(
            value_type="NA",
            elem_type="phy",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_E1(self, buff_info: BuffInfo):
        """冰潮的涡旋·冷酷之心"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"冷酷之心状态下，防御+{30*s}%(+{self.prop.def_base*0.3*s})",
            defense=PoFValue(percent=0.3 * s),
        )

    def buff_E2(self, buff_info: BuffInfo):
        """冰潮的涡旋-减抗"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        scaler = float(
            self.get_scaler("冰潮的涡旋", self.talents[1].level, "物理抗性降低").replace("%", "")
        )
        buff_info.buff = Buff(
            dsc=f"消耗冷酷之心7秒内，物抗、冰抗-{scaler}%，",
            resist_reduction=DmgBonus(phy=scaler, cryo=scaler),
        )

    def skill_Q(self, dmg_info: Dmg):
        """凝浪之光剑"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("凝浪之光剑", self.talents[2].level, "光降之剑基础伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="phy",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_Q(self, buff_info: BuffInfo):
        """凝浪之光剑"""
        setting = buff_info.setting
        if setting.label.isdigit():
            s = min(int(setting.label), 30)
            setting.state = f"{s}层能量"
        else:
            setting.state, s = "×", 0
        scaler = float(
            self.get_scaler("凝浪之光剑", self.talents[2].level, "每层能量伤害").replace("%", "")
        )
        buff_info.buff = Buff(
            dsc=f"光降之剑每层能量倍率+{scaler*s}%",
            target="Q",
            multiplier=Multiplier(atk=scaler * s),
        )

    category: str = "站场物理C"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["站场物理C"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "站场物理C":
                return ["攻击", "攻击%", "物伤", "暴击", "暴伤"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        output.append(self.setting_conduct(labels))
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="光潮的幻象",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("光潮的幻象", "○")),
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="自卑者的逞强",
                        setting=BuffSetting(label=labels.get("自卑者的逞强", "○")),
                    )
                )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="冰潮的涡旋·冷酷之心",
                buff_type="propbuff",
                setting=BuffSetting(
                    dsc="冷酷之心层数，最大两层",
                    label=labels.get("冰潮的涡旋·冷酷之心", "2"),
                ),
            )
        )
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="冰潮的涡旋-减抗",
                buff_range="all",
                setting=BuffSetting(label=labels.get("冰潮的涡旋", "○")),
            )
        )
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="凝浪之光剑",
                setting=BuffSetting(
                    dsc="光降之剑能量层数，上限30",
                    label=labels.get("凝浪之光剑", "14"),
                ),
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "超导":
                    self.buff_conduct(buff)
                case "光潮的幻象":
                    self.buff_C1(buff)
                case "自卑者的逞强":
                    self.buff_C4(buff)
                case "冰潮的涡旋·冷酷之心":
                    self.buff_E1(buff)
                case "冰潮的涡旋-减抗":
                    self.buff_E2(buff)
                case "凝浪之光剑":
                    self.buff_Q(buff)

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
                name="西风剑术·宗室",
                dsc="A首段",
                weight=weights.get("西风剑术·宗室", 0),
                exclude_buff=ex_buffs.get("西风剑术·宗室", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="凝浪之光剑",
                dsc="Q光降之剑",
                weight=weights.get("凝浪之光剑", 0),
                exclude_buff=ex_buffs.get("凝浪之光剑", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "西风剑术·宗室":
                        self.skill_A(dmg)
                    case "凝浪之光剑":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "站场物理C":
                return {
                    "充能效率阈值": 120,
                    "西风剑术·宗室": 10,
                    "凝浪之光剑": 10,
                }
            case _:
                return {
                    "充能效率阈值": 120,
                    "西风剑术·宗室": 10,
                    "凝浪之光剑": 10,
                }

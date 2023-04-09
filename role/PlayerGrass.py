from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, DmgBonus, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class PlayerGrass(Role):
    name = "草主"

    def buff_T1(self, buff_info: BuffInfo):
        """蔓生的埜草"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"草灯莲每秒叠层获得莲光遍照，场上角色共获得精通{6*s}",
            elem_mastery=6 * s,
        )

    T2_E_bonus: float = 0.0
    """T2草缘剑增伤"""
    T2_Q_bonus: float = 0.0
    """T2偃草若化增伤"""

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """繁庑的丛草"""
        dmg_bonus1 = prop.elem_mastery * 0.15 / 100
        dmg_bonus2 = prop.elem_mastery * 0.1 / 100
        buff_info.buff = Buff(
            dsc=f"基于元素精通，草缘剑增伤+{dmg_bonus1:.1%}，偃草若化增伤+{dmg_bonus2:.1%}",
        )
        self.T2_E_bonus = dmg_bonus1
        self.T2_Q_bonus = dmg_bonus2

    def buff_C6(self, buff_info: BuffInfo):
        """蕴思的霜草"""
        setting = buff_info.setting
        buff_info.buff = Buff(
            dsc="莲光遍照影响下，草伤+12%",
            elem_dmg_bonus=DmgBonus(dendro=0.12),
        )
        match setting.label:
            case x if x in ["火", "水", "雷"]:
                setting.state = f"{x}转化"
                buff_info.buff.dsc += f"发生{setting.state}，{x}伤+12%"
                buff_info.buff.elem_dmg_bonus.set({x: 0.12})

    def skill_E(self, dmg_info: Dmg, reaction=""):
        """草缘剑"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("草缘剑", self.talents[1].level, "技能伤害").replace("%", "")
        )
        calc.dmg_bonus = self.T2_E_bonus
        calc.set(
            value_type="E",
            elem_type="dendro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q(self, dmg_info: Dmg, reaction=""):
        """偃草若化"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("偃草若化", self.talents[2].level, "草灯莲攻击伤害").replace("%", "")
        )
        calc.dmg_bonus = self.T2_Q_bonus
        calc.set(
            value_type="Q",
            elem_type="dendro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    category: str = "副C"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["副C", "激化副C"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "副C":
                return ["攻击", "攻击%", "草伤", "暴击", "暴伤", "充能"]
            case "激化副C":
                return ["攻击", "攻击%", "草伤", "暴击", "暴伤", "充能", "精通"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="蔓生的埜草",
                    buff_range="all",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="莲光遍照层数：⓪~⑩每层场上角色精通+6",
                        label=labels.get("蔓生的埜草", "10"),
                    ),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="繁庑的丛草",
                    )
                )
        # 命座
        if self.info.constellation >= 6:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C6",
                    name="蕴思的霜草",
                    buff_range="all",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="元素转化（火，水，雷）：对应元素增伤+12%",
                        label=labels.get("蕴思的霜草", "火"),
                    ),
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "蔓生的埜草":
                    self.buff_T1(buff)
                case "繁庑的丛草":
                    self.buff_T2(buff, prop)
                case "蕴思的霜草":
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
                name="草缘剑",
                dsc="E一段",
                weight=weights.get("草缘剑", 0),
                exclude_buff=ex_buffs.get("草缘剑", []),
            ),
            Dmg(
                index=2,
                source="E",
                name="草缘剑-激化",
                dsc="E一段激化",
                weight=weights.get("草缘剑-激化", 0),
                exclude_buff=ex_buffs.get("草缘剑-激化", []),
            ),
            Dmg(
                index=3,
                source="Q",
                name="偃草若化",
                dsc="Q草灯莲每下",
                weight=weights.get("偃草若化", 0),
                exclude_buff=ex_buffs.get("偃草若化", []),
            ),
            Dmg(
                index=4,
                source="Q",
                name="偃草若化-激化",
                dsc="Q草灯莲每下激化",
                weight=weights.get("偃草若化-激化", 0),
                exclude_buff=ex_buffs.get("偃草若化-激化", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "草缘剑":
                        self.skill_E(dmg)
                    case "草缘剑-激化":
                        self.skill_E(dmg, "蔓激化")
                    case "偃草若化":
                        self.skill_Q(dmg)
                    case "偃草若化-激化":
                        self.skill_Q(dmg, "蔓激化")
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "副C":
                return {
                    "充能效率阈值": 200,
                    "草缘剑": 10,
                    "草缘剑-激化": 0,
                    "偃草若化": 10,
                    "偃草若化-激化": 0,
                }
            case "激化副C":
                return {
                    "充能效率阈值": 200,
                    "草缘剑": 0,
                    "草缘剑-激化": 10,
                    "偃草若化": 0,
                    "偃草若化-激化": 10,
                }
            case _:
                return {
                    "充能效率阈值": 180,
                    "草缘剑": 10,
                    "草缘剑-激化": 10,
                    "偃草若化": 10,
                    "偃草若化-激化": 10,
                }

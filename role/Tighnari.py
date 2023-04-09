from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, DmgBonus, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class Tighnari(Role):
    name = "提纳里"

    def buff_T1(self, buff_info: BuffInfo):
        """眼识殊明"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="发射花筥箭4秒内，精通+50",
            elem_mastery=50,
        )

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """诸叶辨通"""
        dmg_bonus = max(prop.elem_mastery * 0.06 / 100, 0.6)
        buff_info.buff = Buff(
            dsc=f"基于元素精通，其重击与造生缠藤箭增伤+{int(dmg_bonus*100)}%",
            target=["CA", "Q"],
            dmg_bonus=dmg_bonus,
        )

    def buff_C1(self, buff_info: BuffInfo):
        """由根须断定肇始"""
        buff_info.buff = Buff(
            dsc="重击暴击+15%",
            target="CA",
            crit_rate=0.15,
        )

    def buff_C2(self, buff_info: BuffInfo):
        """由茎干剖析来缘"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="识蕴领域中存在敌人6秒内，草伤+20%",
            elem_dmg_bonus=DmgBonus(dendro=0.2),
        )

    def buff_C4(self, buff_info: BuffInfo):
        """由片叶管窥枯荣"""
        setting = buff_info.setting
        match setting.label:
            case "1":
                setting.state, elem_ma = "未触发草反应", 60
            case "2":
                setting.state, elem_ma = "触发草反应", 120
            case _:
                setting.state, elem_ma = "×", 0
        buff_info.buff = Buff(
            dsc=f"施放造生缠藤箭8秒内，所有角色精通+{elem_ma}",
            elem_mastery=elem_ma,
        )

    def skill_A(self, dmg_info: Dmg, reaction=""):
        """藏蕴破障"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("普通攻击·藏蕴破障", self.talents[0].level, "花筥箭伤害").replace(
                "%", ""
            )
        )
        calc.set(
            value_type="CA",
            elem_type="dendro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q(self, dmg_info: Dmg, reaction=""):
        """造生缠藤箭"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("造生缠藤箭", self.talents[2].level, "缠藤箭伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="dendro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    category: str = "激化速切"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["激化速切"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "激化速切":
                return ["攻击", "攻击%", "草伤", "暴击", "暴伤", "精通"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="眼识殊明",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("眼识殊明", "○")),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="诸叶辨通",
                    )
                )
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="由根须断定肇始",
                    buff_type="propbuff",
                )
            )
            if self.info.constellation >= 2:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C2",
                        name="由茎干剖析来缘",
                        buff_type="propbuff",
                        setting=BuffSetting(label=labels.get("由茎干剖析来缘", "○")),
                    )
                )
                if self.info.constellation >= 4:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C4",
                            name="由片叶管窥枯荣",
                            buff_range="all",
                            buff_type="propbuff",
                            setting=BuffSetting(
                                dsc="造生缠藤箭①施放后，精通+60②触发草反应，额外精通+60",
                                label=labels.get("由片叶管窥枯荣", "2"),
                            ),
                        )
                    )
                    # TODO:6命
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "眼识殊明":
                    self.buff_T1(buff)
                case "诸叶辨通":
                    self.buff_T2(buff)
                case "由根须断定肇始":
                    self.buff_C1(buff)
                case "由茎干剖析来缘":
                    self.buff_C2(buff)
                case "由片叶管窥枯荣":
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
                name="藏蕴破障",
                dsc="A花筥箭一段激化",
                weight=weights.get("藏蕴破障", 0),
                exclude_buff=ex_buffs.get("藏蕴破障", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="造生缠藤箭",
                dsc="Q缠藤箭一段激化",
                weight=weights.get("造生缠藤箭", 0),
                exclude_buff=ex_buffs.get("造生缠藤箭", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "藏蕴破障":
                        self.skill_A(dmg, "蔓激化")
                    case "造生缠藤箭":
                        self.skill_Q(dmg, "蔓激化")
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "激化速切":
                return {
                    "充能效率阈值": 100,
                    "藏蕴破障": 10,
                    "造生缠藤箭": 10,
                }
            case _:
                return {
                    "充能效率阈值": 100,
                    "藏蕴破障": 10,
                    "造生缠藤箭": 10,
                }

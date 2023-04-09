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


class Hutao(Role):
    name = "胡桃"

    def buff_T1(self, buff_info: BuffInfo):
        """蝶隐之时"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="彼岸蝶舞结束8秒内，队友暴击+12%",
            crit_rate=0.12,
        )

    def buff_T2(self, buff_info: BuffInfo):
        """血之灶火"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="生命值低于一半时,火伤+33%",
            elem_dmg_bonus=DmgBonus(pyro=0.2),
        )

    def buff_C4(self, buff_info: BuffInfo):
        """伴君眠花房"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="血梅香状态下击败敌方15秒内，队友暴击+12%",
            crit_rate=0.12,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """幽蝶能留一缕芳"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="收到致命伤10秒内，暴击+100%",
            crit_rate=1,
        )

    def skill_A(self, dmg_info: Dmg, reaction=""):
        """往生秘传枪法"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("普通攻击·往生秘传枪法", self.talents[0].level, "重击伤害").replace(
                "%", ""
            )
        )
        calc.set(
            value_type="CA",
            elem_type="pyro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_E(self, buff_info: BuffInfo):
        """蝶引来生"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("蝶引来生", self.talents[1].level, "攻击力提高").replace(
                "%生命值上限", ""
            )
        )
        atk = scaler * calc.calc_trans.hp / 100
        buff_info.buff = Buff(
            dsc=f"基于生命值{scaler}%，提高攻击力(+{atk})",
            atk=PoFValue(fix=atk),
        )

    def skill_Q(self, dmg_info: Dmg, reaction=""):
        """安神秘法"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("安神秘法", self.talents[2].level, "低血量时技能伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="pyro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    category: str = "蒸胡"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["蒸胡"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case x if x in ["蒸胡"]:
                return ["生命%", "生命", "攻击%", "火伤", "暴击", "暴伤", "精通"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="蝶隐之时",
                    buff_range="party",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("蝶隐之时", "○")),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="血之灶火",
                        buff_type="propbuff",
                        setting=BuffSetting(label=labels.get("血之灶火", "○")),
                    )
                )
        # 命座
        if self.info.constellation >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C4",
                    name="伴君眠花房",
                    buff_range="party",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("伴君眠花房", "○")),
                )
            )
            if self.info.constellation >= 6:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C6",
                        name="幽蝶能留一缕芳",
                        buff_type="propbuff",
                        setting=BuffSetting(label=labels.get("幽蝶能留一缕芳", "○")),
                    )
                )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="蝶引来生",
                buff_type="transbuff",
                setting=BuffSetting(label=labels.get("蝶引来生", "○")),
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "蝶隐之时":
                    self.buff_T1(buff)
                case "血之灶火":
                    self.buff_T2(buff)
                case "伴君眠花房":
                    self.buff_C4(buff)
                case "幽蝶能留一缕芳":
                    self.buff_C6(buff)
                case "蝶引来生":
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
                name="往生秘传枪法-蒸发",
                dsc="重击",
                weight=weights.get("往生秘传枪法-蒸发", 0),
                exclude_buff=ex_buffs.get("往生秘传枪法-蒸发", []),
            ),
            # Dmg(
            #     index=2,
            #     source="Q",
            #     name="安神秘法-蒸发",
            #     dsc="Q一段",
            #     weight=weights.get("安神秘法-蒸发", 0),
            #     exclude_buff=ex_buffs.get("安神秘法-蒸发", []),
            # ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "往生秘传枪法-蒸发":
                        self.skill_A(dmg, "蒸发")
                    case "安神秘法-蒸发":
                        self.skill_Q(dmg, "蒸发")
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "蒸胡":
                return {
                    "充能效率阈值": 100,
                    "往生秘传枪法-蒸发": 10,
                    "安神秘法-蒸发": -1,
                }
            case _:
                return {
                    "充能效率阈值": 100,
                    "往生秘传枪法-蒸发": 10,
                }

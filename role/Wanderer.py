from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, Multiplier
from ._model import Role


class Wanderer(Role):
    name = "流浪者"

    def buff_T1(self, buff_info: BuffInfo):
        """拾玉得花"""
        buff_info.buff = Buff(
            dsc="施放羽画·风姿华歌时",
        )
        max_buff = 3 if self.info.constellation >= 4 else 2
        setting = buff_info.setting
        for label in setting.label[:max_buff]:
            match label:
                case "火":
                    setting.state += "火"
                    buff_info.buff.dsc += f"，接触火元素，攻击+30%({self.prop.atk_base*0.3})%"
                    buff_info.buff.atk.percent = 0.3
                case "水":
                    setting.state += "水"
                case "雷":
                    setting.state += "雷"
                case "冰":
                    setting.state += "冰"
                    buff_info.buff.dsc += "，接触冰元素，暴击+20%"
                    buff_info.buff.crit_rate = 0.2
        setting.state += "强化"

    def buff_C2(self, buff_info: BuffInfo):
        """二番·箙岛月白浪"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="优风倾姿状态下，依据消耗的空居力，狂言·式乐五番最大增伤+200%",
            target="Q",
            dmg_bonus=2,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """四番·花月歌浮舟"""
        buff_info.buff = Buff(
            dsc="拾玉得花元素效果上限提升为3种",
        )

    def skill_A1(self, dmg_info: Dmg):
        """行幡鸣弦·普攻"""
        calc = self.create_calc()
        scaler1, scaler2 = [
            float(i.replace("%", "")) / 100
            for i in self.get_scaler(
                "普通攻击·行幡鸣弦",
                self.talents[0].level,
                "一段伤害",
                "二段伤害",
            )
        ]
        calc.set(
            value_type="NA",
            elem_type="anemo",
            multiplier=Multiplier(atk=(scaler1 + scaler2) * self.E_NA_scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_A2(self, dmg_info: Dmg):
        """行幡鸣弦·重击"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("普通攻击·行幡鸣弦", self.talents[0].level, "重击伤害").replace("%", "")
        )
        calc.set(
            value_type="CA",
            elem_type="anemo",
            multiplier=Multiplier(atk=scaler * self.E_CA_scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    E_NA_scaler: float = 1.0
    """空居·不生断倍率器"""
    E_CA_scaler: float = 1.0
    """空居·刀风界倍率器"""

    def buff_E(self, buff_info: BuffInfo):
        """羽画·风姿华歌"""
        self.E_NA_scaler, self.E_CA_scaler = [
            float(i.replace("%", "")) / 100
            for i in self.get_scaler(
                "羽画·风姿华歌",
                self.talents[1].level,
                "空居·不生断伤害",
                "空居·刀风界伤害",
            )
        ]
        buff_info.buff = Buff(
            dsc="进入「优风倾姿」状态，普攻倍率x{self.E_NA_scaler:.1%}，重击倍率x{self.E_CA_scaler:.1%}",
        )

    def skill_Q(self, dmg_info: Dmg):
        """狂言·式乐五番"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("狂言·式乐五番", self.talents[2].level, "技能伤害").replace("%×5", "")
        )
        calc.set(
            value_type="Q",
            elem_type="anemo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    category: str = "站场风C"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["站场风C"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "站场风C":
                return ["攻击", "攻击%", "风伤", "暴击", "暴伤"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="拾玉得花",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="触发狂言·式乐五番（火，水，雷，冰）：对应元素增伤基于元素精通，可共存",
                        label=labels.get("拾玉得花", "火"),
                    ),
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="二番·箙岛月白浪",
                    setting=BuffSetting(label=labels.get("二番·箙岛月白浪", "○")),
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="四番·花月歌浮舟",
                    )
                )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="羽画·风姿华歌",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "拾玉得花":
                    self.buff_T1(buff)
                case "二番·箙岛月白浪":
                    self.buff_C2(buff)
                case "四番·花月歌浮舟":
                    self.buff_C4(buff)
                case "羽画·风姿华歌":
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
                name="行幡鸣弦·普攻",
                dsc="空居·不生断前两段",
                weight=weights.get("行幡鸣弦·普攻", 0),
                exclude_buff=ex_buffs.get("行幡鸣弦·普攻", []),
            ),
            Dmg(
                index=1,
                source="A",
                name="行幡鸣弦·重击",
                dsc="空居·刀风界",
                weight=weights.get("行幡鸣弦·重击", 0),
                exclude_buff=ex_buffs.get("行幡鸣弦·重击", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="狂言·式乐五番",
                dsc="Q每段",
                weight=weights.get("狂言·式乐五番", 0),
                exclude_buff=ex_buffs.get("狂言·式乐五番", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "行幡鸣弦·普攻":
                        self.skill_A1(dmg)
                    case "行幡鸣弦·重击":
                        self.skill_A2(dmg)
                    case "狂言·式乐五番":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "站场风C":
                return {
                    "充能效率阈值": 100,
                    "行幡鸣弦·普攻": 10,
                    "行幡鸣弦·重击": 10,
                    "狂言·式乐五番": 10,
                }

from ..classmodel import Dmg, Buff, BuffInfo, BuffSetting, DmgBonus, Multiplier
from ._model import Role


class Venti(Role):
    name = "温迪"

    def buff_C2(self, buff_info: BuffInfo):
        """眷恋的泠风"""
        setting = buff_info.setting
        match setting.label:
            case "1":
                buff_info.buff = Buff(
                    dsc="高天之歌命中10秒内，风抗，物抗-12%",
                    resist_reduction=DmgBonus(phy=0.12, anemo=0.12),
                )
            case "2":
                setting.state = "击飞中"
                buff_info.buff = Buff(
                    dsc="高天之歌击飞落地前，风抗，物抗-24%",
                    resist_reduction=DmgBonus(phy=0.24, anemo=0.24),
                )
            case _:
                setting.state = "×"

    def buff_C4(self, buff_info: BuffInfo):
        """自由的凛风"""
        buff_info.buff = Buff(
            dsc="获取元素球10秒内，风伤+25%",
            elem_dmg_bonus=DmgBonus(anemo=0.25),
        )

    def buff_C6(self, buff_info: BuffInfo):
        """抗争的暴风"""
        setting = buff_info.setting
        buff_info.buff = Buff(
            dsc="风神之诗命中，风抗-20%",
            resist_reduction=DmgBonus(anemo=0.2),
        )
        match setting.label:
            case x if x in ["火", "水", "雷", "冰"]:
                setting.state = f"{x}风"
                buff_info.buff.dsc += f"，{x}抗-20%"
                buff_info.buff.resist_reduction.set({x: 0.2})

    def skill_E(self, dmg_info: Dmg):
        """高天之歌"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("高天之歌", self.talents[1].level, "点按伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="anemo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q(self, dmg_info: Dmg):
        """风神之诗"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("风神之诗", self.talents[2].level, "持续伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="anemo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def swirls(self, dmg_info: Dmg):
        """扩散伤害"""
        calc = self.create_calc()
        calc.set(
            reaction_type="扩散",
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_trans_reac_dmg())

    category: str = "充能副核"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["充能副核", "精通副核"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        match self.category:
            case "充能副核":
                return ["攻击", "攻击%", "风伤", "暴击", "暴伤", "充能"]
            case "精通副核":
                return ["充能", "精通"]
            case _:
                return ["攻击%", "风伤", "暴击", "暴伤", "充能", "精通"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="眷恋的泠风",
                    buff_range="all",
                    setting=BuffSetting(
                        dsc="高天之歌击飞，①（✓）：风抗，物抗-12%；②落地前：额外风抗，物抗-12%",
                        label=labels.get("眷恋的泠风", "1"),
                    ),
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="自由的凛风",
                        buff_type="propbuff",
                        setting=BuffSetting(label=labels.get("自由的凛风", "○")),
                    )
                )
                if self.info.constellation >= 6:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C6",
                            name="抗争的暴风",
                            buff_range="all",
                            setting=BuffSetting(
                                dsc="元素转化①火②水③雷④冰：对应抗性-20%",
                                label=labels.get("抗争的暴风", "火"),
                            ),
                        )
                    )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "眷恋的泠风":
                    self.buff_C2(buff)
                case "自由的凛风":
                    self.buff_C4(buff)
                case "抗争的暴风":
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
                name="高天之歌",
                dsc="E点按",
                weight=weights.get("高天之歌", 0),
                exclude_buff=ex_buffs.get("高天之歌", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="风神之诗",
                dsc="Q风伤每段",
                weight=weights.get("风神之诗", 0),
                exclude_buff=ex_buffs.get("风神之诗", []),
            ),
            Dmg(
                index=3,
                name="扩散",
                dsc="扩散伤害",
                weight=weights.get("扩散", 0),
                exclude_buff=ex_buffs.get("扩散", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "高天之歌":
                        self.skill_E(dmg)
                    case "风神之诗":
                        self.skill_Q(dmg)
                    case "扩散":
                        self.swirls(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "充能副核":
                return {
                    "充能效率阈值": 200,
                    "高天之歌": 10,
                    "风神之诗": -1,
                    "扩散": -1,
                }
            case "精通副核":
                return {
                    "充能效率阈值": 240,
                    "高天之歌": 0,
                    "风神之诗": 0,
                    "扩散": 10,
                }
            case _:
                return {
                    "充能效率阈值": 200,
                    "高天之歌": 5,
                    "风神之诗": 5,
                    "扩散": 5,
                }

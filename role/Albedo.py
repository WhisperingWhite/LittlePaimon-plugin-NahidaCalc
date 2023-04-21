from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, Multiplier
from ._model import Role


class Albedo(Role):
    name = "阿贝多"

    def buff_T1(self, buff_info: BuffInfo):
        """白垩色的威压"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="对生命低于50%的敌人，刹那之花增伤+25%",
            target="E",
            dmg_bonus=0.25,
        )

    def buff_T2(self, buff_info: BuffInfo):
        """瓶中人的天慧"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="释放诞生式·大地之潮10秒内,全队精通+125",
            elem_mastery=125,
        )

    def buff_C2(self, buff_info: BuffInfo):
        """显生之宙"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        scaler = s * 30
        buff_info.buff = Buff(
            dsc=f"诞生式·大地之潮与生灭之花，倍率+{scaler}%防御力",
            target="Q",
            multiplier=Multiplier(defense=scaler),
        )

    def buff_C4(self, buff_info: BuffInfo):
        """神性之陨"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="阳华的领域中，场上角色下落增伤+30%",
            target="PA",
            dmg_bonus=0.3,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """无垢之土"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="阳华的领域中，在结晶盾庇护下，场上角色增伤+17%",
            dmg_bonus=0.17,
        )

    def skill_E(self, dmg_info: Dmg):
        """创生法·拟造阳华"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("创生法·拟造阳华", self.talents[1].level, "刹那之花伤害").replace(
                "%防御力", ""
            )
        )
        calc.set(
            value_type="E",
            elem_type="geo",
            multiplier=Multiplier(defense=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q1(self, dmg_info: Dmg):
        """诞生式·大地之潮"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("诞生式·大地之潮", self.talents[2].level, "爆发伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="geo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q2(self, dmg_info: Dmg):
        """诞生式·大地之潮·生灭之花"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("诞生式·大地之潮", self.talents[2].level, "生灭之花")
            .replace("%", "")
            .replace("每朵", "")
        )
        calc.set(
            value_type="Q",
            elem_type="geo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    category: str = "后台岩C"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["后台岩C"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "后台岩C":
                return ["防御", "防御%", "攻击%", "岩伤", "暴击", "暴伤"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="白垩色的威压",
                    setting=BuffSetting(label=labels.get("白垩色的威压", "○")),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="瓶中人的天慧",
                        buff_range="all",
                        buff_type="propbuff",
                        setting=BuffSetting(label=labels.get("瓶中人的天慧", "○")),
                    )
                )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="显生之宙",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="刹那之花绽放时，赋予生灭计数，⓪~④每层元素爆发基础伤害+30%防御力",
                        label=labels.get("显生之宙", "4"),
                    ),
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="神性之陨",
                        buff_range="all",
                        setting=BuffSetting(label=labels.get("神性之陨", "○")),
                    )
                )
                if self.info.constellation >= 6:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C6",
                            name="无垢之土",
                            buff_range="all",
                            setting=BuffSetting(label=labels.get("无垢之土", "○")),
                        )
                    )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "白垩色的威压":
                    self.buff_T1(buff)
                case "瓶中人的天慧":
                    self.buff_T2(buff)
                case "显生之宙":
                    self.buff_C2(buff)
                case "神性之陨":
                    self.buff_C4(buff)
                case "无垢之土":
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
                name="创生法·拟造阳华",
                dsc="E刹那之花单段",
                weight=weights.get("创生法·拟造阳华", 0),
                exclude_buff=ex_buffs.get("创生法·拟造阳华", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="诞生式·大地之潮",
                dsc="Q爆发单段",
                weight=weights.get("诞生式·大地之潮", 0),
                exclude_buff=ex_buffs.get("诞生式·大地之潮", []),
            ),
            Dmg(
                index=3,
                source="Q",
                name="诞生式·大地之潮·生灭之花",
                dsc="Q生灭之花每朵",
                weight=weights.get("诞生式·大地之潮·生灭之花", 0),
                exclude_buff=ex_buffs.get("诞生式·大地之潮·生灭之花", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "创生法·拟造阳华":
                        self.skill_E(dmg)
                    case "诞生式·大地之潮":
                        self.skill_Q1(dmg)
                    case "诞生式·大地之潮·生灭之花":
                        self.skill_Q2(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "后台岩C":
                return {
                    "充能效率阈值": 100,
                    "创生法·拟造阳华": 10,
                    "诞生式·大地之潮": 0,
                    "诞生式·大地之潮·生灭之花": 0,
                }
            case _:
                return {
                    "充能效率阈值": 120,
                    "创生法·拟造阳华": 10,
                    "诞生式·大地之潮": -1,
                    "诞生式·大地之潮·生灭之花": -1,
                }

from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class Nahida(Role):
    name = "纳西妲"

    def buff_T1(self, buff_info: BuffInfo, prop: DmgCalc):
        """净善摄受明论"""
        setting = buff_info.setting
        if setting.label.isdigit():
            ext_elem_ma = float(setting.label)
        else:
            ext_elem_ma = 0
        elem_ma = min(max(prop.elem_mastery * 0.25, ext_elem_ma), 250)
        setting.state = "最高精通" + str(elem_ma)
        buff_info.buff = Buff(
            dsc=f"摩耶之殿领域内，场上角色精通+{elem_ma:.0f}",
            elem_mastery=elem_ma,
        )

    def Skill_T1(self, dmg_info: Dmg):
        """净善摄受明论"""
        calc = self.create_calc()
        elem_ma = min(calc.calc_dmg.elem_mastery * 0.25, 250)
        dmg_info.exp_value = elem_ma

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """慧明缘觉智论"""
        dmg_bonus = min((prop.elem_mastery - 200) * 0.1 / 100, 0.8)
        crit_rate = min((prop.elem_mastery - 200) * 0.03 / 100, 0.24)
        buff_info.buff = Buff(
            dsc=f"灭净三业增伤+{(dmg_bonus*100):.1f}%，暴击+{(dmg_bonus*100):.1f}%",
            target="E",
            dmg_bonus=dmg_bonus,
            crit_rate=crit_rate,
        )

    def buff_C1(self, buff_info: BuffInfo):
        """心识蕴藏之种"""
        buff_info.buff = Buff(
            dsc="摩耶之殿领域额外计入火、雷、水各1名",
        )

    def buff_C2(self, buff_info: BuffInfo):
        """正等善见之根"""
        buff_info.buff = Buff(
            dsc="蕴种印状态下，触发激化系列反应8秒内，减防+30%",
            def_reduction=0.3,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """比量现行之茎"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4"]:
                setting.state, elem_ma = f"链接{x}名", 80 + 20 * int(x)
            case _:
                setting.state, elem_ma = "×", 0
        buff_info.buff = Buff(
            dsc=f"基于蕴种印链接数量，精通+{elem_ma}",
            elem_mastery=elem_ma,
        )

    def skill_E(self, dmg_info: Dmg, reaction=""):
        """所闻遍计"""
        calc = self.create_calc()
        scaler1, scaler2 = [
            float(num)
            for num in self.get_scaler("所闻遍计", self.talents[1].level, "灭净三业伤害")
            .replace("%攻击力", "")
            .replace("%元素精通", "")
            .split("+")
        ]
        calc.set(
            value_type="E",
            elem_type="dendro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler1, em=scaler2),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_E_C6(self, dmg_info: Dmg, reaction=""):
        """灭净三业·业障除"""
        calc = self.create_calc()
        calc.set(
            value_type="E",
            elem_type="dendro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=200, em=400),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_Q(self, buff_info: BuffInfo):
        """心景幻成"""
        fire = 1 if self.info.constellation >= 1 else 0
        setting = buff_info.setting
        for label in setting.label[0:3]:
            match label:
                case x if x in ["火", "雷", "水"]:
                    setting.state += x
                    if x == "火":
                        fire += 1
                case _:
                    setting.state = ("×",)
        scaler1 = float(
            self.get_scaler("心景幻成", self.talents[2].level, "火：伤害提升1").replace("%", "")
        )
        scaler2 = float(
            self.get_scaler("心景幻成", self.talents[2].level, "火：伤害提升2").replace("%", "")
        )
        fire = min(fire, 2)
        match fire:
            case 1:
                scaler = scaler1
            case 2:
                scaler = scaler2
            case _:
                scaler = 0
        buff_info.buff = Buff(
            dsc=f"摩耶之殿领域内，灭净三业增伤+{scaler}%",
            target="E",
            dmg_bonus=scaler / 100,
        )

    category: str = "后台副C"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["精通拐", "后台副C"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "精通拐":
                return ["充能", "精通"]
            case "后台副C":
                return ["攻击%", "草伤", "暴击", "暴伤", "充能", "精通"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="净善摄受明论",
                    buff_range="active",
                    buff_type="transbuff",
                    setting=BuffSetting(
                        dsc="摩耶之殿提升精通，基于队伍中的最高精通（0-1000）",
                        label=labels.get("净善摄受明论", "0"),
                    ),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="慧明缘觉智论",
                    )
                )
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="心识蕴藏之种",
                )
            )
            if self.info.constellation >= 2:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C2",
                        name="正等善见之根",
                        buff_range="all",
                    )
                )
                if self.info.constellation >= 4:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C4",
                            name="比量现行之茎",
                            buff_range="all",
                            buff_type="propbuff",
                            setting=BuffSetting(
                                dsc="蕴种印链接的敌方数量，①~④精通+100/120/140/160",
                                label=labels.get("比量现行之茎", "4"),
                            ),
                        )
                    )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="心景幻成",
                setting=BuffSetting(
                    dsc="队伍中角色元素类型（火、水、雷），产生对应效果",
                    label=labels.get("比量现行之茎", "水雷"),
                ),
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "净善摄受明论":
                    self.buff_T1(buff, prop)
                case "慧明缘觉智论":
                    self.buff_T2(buff, prop)
                case "心识蕴藏之种":
                    self.buff_C1(buff)
                case "正等善见之根":
                    self.buff_C2(buff)
                case "比量现行之茎":
                    self.buff_C4(buff)
                case "心景幻成":
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
                source="T1",
                name="净善摄受明论",
                dsc="摩耶之殿领域内额外精通",
                weight=weights.get("净善摄受明论", 0),
                exclude_buff=ex_buffs.get("净善摄受明论", []),
            ),
            Dmg(
                index=2,
                source="E",
                name="所闻遍计",
                dsc="E灭净三业每次",
                weight=weights.get("所闻遍计", 0),
                exclude_buff=ex_buffs.get("所闻遍计", []),
            ),
            Dmg(
                index=3,
                source="E",
                name="所闻遍计-激化",
                dsc="E灭净三业每次激化",
                weight=weights.get("所闻遍计-激化", 0),
                exclude_buff=ex_buffs.get("所闻遍计-激化", []),
            ),
        ]
        if self.info.constellation == 6:
            self.dmg_list.append(
                Dmg(
                    index=4,
                    source="E",
                    name="灭净三业·业障除",
                    dsc="E每次激化",
                    weight=weights.get("灭净三业·业障除", 0),
                    exclude_buff=ex_buffs.get("灭净三业·业障除", []),
                )
            )

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "净善摄受明论":
                        self.skill_T1(dmg)
                    case "所闻遍计":
                        self.skill_E(dmg)
                    case "所闻遍计-激化":
                        self.skill_E(dmg, "蔓激化")
                    case "灭净三业·业障除":
                        self.skill_E_C6(dmg, "蔓激化")
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "精通拐":
                return {
                    "充能效率阈值": 180,
                    "净善摄受明论": 10,
                    "所闻遍计": -1,
                    "所闻遍计-激化": 0,
                    "灭净三业·业障除": 0,
                }
            case "后台副C":
                return {
                    "充能效率阈值": 140,
                    "净善摄受明论": 0,
                    "所闻遍计": -1,
                    "所闻遍计-激化": 10,
                    "灭净三业·业障除": 10,
                }
            case _:
                return {
                    "充能效率阈值": 150,
                    "净善摄受明论": 0,
                    "所闻遍计": -1,
                    "所闻遍计-激化": 10,
                    "灭净三业·业障除": 10,
                }

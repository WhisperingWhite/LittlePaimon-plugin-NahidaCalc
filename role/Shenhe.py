from ..classmodel import (
    Buff,
    BuffInfo,
    BuffSetting,
    Dmg,
    DmgBonus,
    Multiplier,
    FixValue,
)
from ..dmg_calc import DmgCalc
from ._model import Role


class Shenhe(Role):
    name = "申鹤"

    def buff_T1(self, buff_info: BuffInfo):
        """大洞弥罗尊法"""
        buff_info.buff = Buff(
            dsc="神女遣灵真诀的领域中，冰伤+15%",
            elem_dmg_bonus=DmgBonus(cryo=0.15),
        )

    def buff_T2(self, buff_info: BuffInfo):
        """缚灵通真法印"""
        setting = buff_info.setting
        buff_info.buff = Buff(dmg_bonus=0.15)
        match setting.label:
            case "10":
                setting.state = "点按"
                buff_info.buff.dsc = "施放仰灵威召将役咒，全队元素战技和元素爆发增伤+15%"
                buff_info.buff.target = ["E", "Q"]
            case "01":
                setting.state = "长按"
                buff_info.buff.dsc = "施放仰灵威召将役咒，全队普攻、重击和下落增伤+15%"
                buff_info.buff.target = ["NA", "CA", "PA"]
            case "11":
                setting.state = "点按和长按"
                buff_info.buff.dsc = "施放仰灵威召将役咒，全队增伤+15%"
            case _:
                setting.state = "×"

    def buff_C2(self, buff_info: BuffInfo):
        """定蒙"""
        buff_info.buff = Buff(
            dsc="神女遣灵真诀的领域中，冰元素伤害的暴伤+15%",
            crit_rate=0.15,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """洞观"""
        setting = buff_info.setting
        if x := setting.label.isdigit():
            setting.state, dmg_bonus = f"{x}层「霜霄诀」", min(int(x), 50) * 0.05
        else:
            setting.state, dmg_bonus = "×", 0
        buff_info.buff = Buff(
            dsc=f"清除所有「霜霄诀」，本次仰灵威召将役咒增伤+{dmg_bonus*100}%",
            target="Q",
            dmg_bonus=dmg_bonus,
        )

    def buff_E(self, buff_info: BuffInfo, prop: DmgCalc):
        """仰灵威召将役咒·冰翎"""
        scaler = float(
            self.get_scaler("仰灵威召将役咒", self.talents[1].level, "伤害值提升").replace("%", "")
        )
        extra_dmg = prop.atk * scaler
        buff_info.buff = Buff(
            dsc=f"消耗冰翎，队友冰元素伤害基础伤害+{extra_dmg}",
            fix_value=FixValue(dmg=extra_dmg),
        )

    def buff_Q(self, buff_info: BuffInfo):
        """神女遣灵真诀·「箓灵」"""
        scaler = float(
            self.get_scaler("神女遣灵真诀", self.talents[2].level, "抗性降低").replace("%", "")
        )
        buff_info.buff = Buff(
            dsc=f"「箓灵」结成领域中，敌人的冰抗与物抗-{scaler}%",
            resist_reduction=DmgBonus(phy=scaler / 100, cryo=scaler / 100),
        )

    def skill_E(self, dmg_info: Dmg):
        """仰灵威召将役咒·冰翎"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("仰灵威召将役咒", self.talents[1].level, "伤害值提升").replace("%", "")
        )
        dmg_info.exp_value = calc.calc_dmg.atk * scaler

    def skill_Q(self, dmg_info: Dmg):
        """神女遣灵真诀"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("神女遣灵真诀", self.talents[2].level, "持续伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="cryo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="大洞弥罗尊法",
                    buff_range="active",
                    buff_type="propbuff",
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="缚灵通真法印",
                        buff_range="all",
                        setting=BuffSetting(
                            dsc="施放仰灵威召将役咒，'10'：点按；'01'：长按",
                            label=labels.get("缚灵通真法印", "10"),
                        ),
                    )
                )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="定蒙",
                    buff_range="active",
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="洞观",
                        setting=BuffSetting(
                            dsc="触发「冰翎」叠层，每层仰灵威召将役咒增伤+5%，上限50层",
                            label=labels.get("洞观", "50"),
                        ),
                    )
                )
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="仰灵威召将役咒·冰翎",
                buff_range="all",
                buff_type="transbuff",
            )
        )
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="神女遣灵真诀·「箓灵」",
                buff_range="all",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "大洞弥罗尊法":
                    self.buff_T1(buff)
                case "缚灵通真法印":
                    self.buff_T2(buff)
                case "定蒙":
                    self.buff_C2(buff)
                case "洞观":
                    self.buff_C4(buff)
                case "仰灵威召将役咒·冰翎":
                    self.buff_E(buff, prop)
                case "神女遣灵真诀·「箓灵」":
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
                source="E",
                name="仰灵威召将役咒",
                type="B",
                dsc="E冰翎基础伤害",
                weight=weights.get("仰灵威召将役咒", 0),
                exclude_buff=ex_buffs.get("仰灵威召将役咒"),
            ),
            Dmg(
                index=2,
                source="Q",
                name="神女遣灵真诀",
                dsc="Q领域每段",
                weight=weights.get("神女遣灵真诀", 0),
                exclude_buff=ex_buffs.get("神女遣灵真诀"),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "仰灵威召将役咒·冰翎":
                        self.skill_E(dmg)
                    case "神女遣灵真诀":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 200,
                    "仰灵威召将役咒·冰翎": 10,
                    "神女遣灵真诀": 5,
                }

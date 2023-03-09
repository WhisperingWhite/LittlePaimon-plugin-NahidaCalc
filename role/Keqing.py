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


class Keqing(Role):
    name = "刻晴"

    def buff_T2(self, buff_info: BuffInfo):
        """玉衡之贵"""
        buff_info.buff = Buff(
            dsc="施放天街巡游8秒内，暴击+15%，充能+15%",
            crit_rate=0.15,
            recharge=0.15,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """调律"""
        buff_info.buff = Buff(
            dsc=f"触发雷反应10秒内，攻击+25%({self.prop.atk_base*0.25:.0f})",
            atk=PoFValue(percent=0.25),
        )

    def buff_C6(self, buff_info: BuffInfo):
        """廉贞"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"{x}层廉贞，雷伤+{s*6}%",
            elem_dmg_bonus=DmgBonus(electro=0.06 * s),
        )

    def skill_E(self, dmg_info: Dmg):
        """星斗归位"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("星斗归位", self.talents[1].level, "斩击伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="electro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q(self, dmg_info: Dmg):
        """天街巡游"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("天街巡游", self.talents[2].level, "最后一击伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="electro",
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
        if self.info.ascension >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T2",
                    name="玉衡之贵",
                    buff_type="propbuff",
                )
            )
        # 命座
        if self.info.constellation >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C4",
                    name="调律",
                    buff_type="propbuff",
                )
            )
            if self.info.constellation >= 6:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C6",
                        name="廉贞",
                        buff_type="propbuff",
                        setting=BuffSetting(
                            dsc="施放普攻、重击、元素战技、元素爆发叠层，①~④每层雷伤+6%",
                            label=labels.get("廉贞", "4"),
                        ),
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "玉衡之贵":
                    self.buff_T2(buff)
                case "调律":
                    self.buff_C4(buff)
                case "廉贞":
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
                name="星斗归位",
                dsc="E瞬移斩击",
                weight=weights.get("星斗归位", 0),
                exclude_buff=ex_buffs.get("星斗归位", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="天街巡游",
                dsc="Q尾斩",
                weight=weights.get("天街巡游", 0),
                exclude_buff=ex_buffs.get("天街巡游", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "星斗归位":
                        self.skill_E(dmg)
                    case "天街巡游":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "星斗归位": -1,
                    "天街巡游": 10,
                }

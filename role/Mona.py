from ..classmodel import (
    Buff,
    BuffInfo,
    BuffSetting,
    Dmg,
    DmgBonus,
    Multiplier,
    ReaFactor,
)
from ..dmg_calc import DmgCalc
from ._model import Role


class Mona(Role):
    name = "莫娜"

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """「托付于命运吧!」"""
        hydro_bonus = (prop.recharge - self.prop.recharge) * 0.2
        buff_info.buff = Buff(
            dsc=f"水伤额外提升充能的20%(+{hydro_bonus*100}%)",
            elem_dmg_bonus=DmgBonus(hydro=hydro_bonus),
        )

    def buff_C1(self, buff_info: BuffInfo):
        """沉没的预言"""
        buff_info.buff = Buff(
            dsc="命中处于星异状态下敌人8秒内，感电、蒸发、水元素扩散反应系数+15%",
            reaction_coeff=ReaFactor(
                vaporize=0.15,
                charged=0.15,
                swirl=0.15,
            ),
        )

    def buff_C4(self, buff_info: BuffInfo):
        """灭绝的预言"""
        buff_info.buff = Buff(
            dsc="攻击星异状态下敌人时，暴击+15%",
            crit_rate=0.15,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """厄运的修辞"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"进入虚实流动叠层，重击增伤+{60*s}%，持续8s",
            target="NA",
            dmg_bonus=0.6 * s,
        )

    def skill_Q(self, dmg_info: Dmg):
        """星命定轨·泡影"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("星命定轨", self.talents[2].level, "泡影破裂伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="hydro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_Q(self, buff_info: BuffInfo):
        """星命定轨·星异"""
        dmg_bonus = float(
            self.get_scaler("星命定轨", self.talents[2].level, "伤害加成").replace("%", "")
        )
        buff_info.buff = Buff(
            dsc=f"星异状态下，增伤+{dmg_bonus}%",
            dmg_bonus=dmg_bonus / 100,
        )

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
                    name="「托付于命运吧!」",
                    buff_type="transbuff",
                )
            )
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="沉没的预言",
                    buff_range="all",
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="灭绝的预言",
                        buff_range="all",
                        buff_type="propbuff",
                    )
                )
                if self.info.constellation >= 6:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C6",
                            name="厄运的修辞",
                            setting=BuffSetting(
                                dsc="进入虚实流动每秒叠层，⓪~③每层重击增伤+60%",
                                label=labels.get("厄运的修辞", "3"),
                            ),
                        )
                    )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="星命定轨",
                buff_range="all",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "「托付于命运吧!」":
                    self.buff_T2(buff, prop)
                case "沉没的预言":
                    self.buff_C1(buff)
                case "灭绝的预言":
                    self.buff_C4(buff)
                case "厄运的修辞":
                    self.buff_C6(buff)
                case "星命定轨":
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
                source="Q",
                name="星命定轨·泡影",
                dsc="Q泡影破裂",
                weight=weights.get("星命定轨·泡影", 0),
                exclude_buff=ex_buffs.get("星命定轨·泡影", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "星命定轨·泡影":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 240,
                    "星命定轨·泡影": -1,
                }

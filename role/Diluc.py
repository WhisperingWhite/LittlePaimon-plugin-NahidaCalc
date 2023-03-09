from ..classmodel import (
    Dmg,
    Buff,
    BuffInfo,
    BuffSetting,
    DmgBonus,
    Multiplier,
    PoFValue,
)
from ._model import Role


class Diluc(Role):
    name = "迪卢克"

    def buff_T2(self, buff_info: BuffInfo):
        """熔毁之翼"""
        buff_info.buff = Buff(
            dsc="释放黎明后4秒内，火伤+20%",
            elem_dmg_bonus=DmgBonus(pyro=0.2),
        )

    def buff_C1(self, buff_info: BuffInfo):
        """罪罚裁断"""
        buff_info.buff = Buff(
            dsc="敌方生命值高于一半，增伤+15%",
            dmg_bonus=0.15,
        )

    def buff_C2(self, buff_info: BuffInfo):
        """炙热余烬"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"受伤叠层后，攻击+{10*s}%({self.prop.atk_base*0.1*s})",
            atk=PoFValue(percent=0.1 * s),
        )

    def buff_C4(self, buff_info: BuffInfo):
        """流火焦灼"""
        buff_info.buff = Buff(
            dsc="释放逆焰之刃2秒后，下段逆焰之刃增伤+40%",
            target="E",
            dmg_bonus=0.4,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """清算黑暗的炎之剑"""
        buff_info.buff = Buff(
            dsc="释放逆焰之刃6秒内，普攻增伤+30%",
            target="NA",
            dmg_bonus=0.3,
        )

    def skill_E(self, dmg_info: Dmg):
        """逆焰之刃"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("逆焰之刃", self.talents[1].level, "一段伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="pyro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff + ["流火焦灼"],
        )
        exp_value1, crit_value1 = calc.calc_dmg.get_dmg()

        scaler = sum(
            [
                float(i.replace("%", ""))
                for i in self.get_scaler(
                    "普通攻击·流天射术",
                    self.talents[1].level,
                    "二段伤害",
                    "三段伤害",
                )
            ]
        )
        calc.multiplier.atk = scaler
        calc.exlude_buffs = dmg_info.exclude_buff
        exp_value2, crit_value2 = calc.calc_dmg.get_dmg()

        dmg_info.exp_value, dmg_info.crit_value = (
            exp_value1 + exp_value2,
            crit_value1 + crit_value2,
        )

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T2",
                    name="熔毁之翼",
                    buff_type="propbuff",
                )
            )
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="罪罚裁断",
                )
            )
            if self.info.constellation >= 2:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C2",
                        name="炙热余烬",
                        buff_type="propbuff",
                        setting=BuffSetting(
                            dsc="受到伤害叠层，⓪~③每层：攻击+10%",
                            label=labels.get("炙热余烬", "3"),
                        ),
                    )
                )
                if self.info.constellation >= 4:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C4",
                            name="流火焦灼",
                        )
                    )
                    if self.info.constellation >= 6:
                        output.append(
                            BuffInfo(
                                source=f"{self.name}-C6",
                                name="清算黑暗的炎之剑",
                            )
                        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "熔毁之翼":
                    self.buff_T2(buff)
                case "罪罚裁断":
                    self.buff_C1(buff)
                case "炙热余烬":
                    self.buff_C2(buff)
                case "流火焦灼":
                    self.buff_C4(buff)
                case "清算黑暗的炎之剑":
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
                name="逆焰之刃",
                dsc="E三段",
                weight=weights.get("逆焰之刃", 0),
                exclude_buff=ex_buffs.get("逆焰之刃", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "逆焰之刃":
                        self.skill_E(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str) -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "逆焰之刃": 10,
                }

from ..classmodel import Dmg, Buff, BuffInfo, BuffSetting, FixValue, Multiplier
from ._model import Role


class Feiyan(Role):
    name = "烟绯"

    def buff_T1(self, buff_info: BuffInfo):
        """甲衣交叠"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4", "5"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"获取或刷新烈烧佑命护盾叠层，场上角色护盾强效+{5*s}，持续6秒",
            shield_strength=0.05 * s,
        )

    def buff_T2(self, buff_info: BuffInfo):
        """烈火攻燔"""
        buff_info.buff = Buff(
            dsc="炽火崩破，倍率+2.2%生命值上限",
            target="Q",
            mutiplier=Multiplier(hp=2.2),
        )

    def buff_C6(self, buff_info: BuffInfo):
        """炽烧的至心"""
        buff_info.buff = Buff(
            dsc="获取或刷新烈烧佑命护盾6秒内，普攻、重击与下落增伤+15%",
            dmg_bonus=0.15,
        )

    def skill_E(self, dmg_info: Dmg):
        """烈烧佑命之侍护"""
        calc = self.create_calc()
        scaler, fix_value = float(
            self.get_scaler("烈烧佑命之侍护", self.talents[1].level, "护盾吸收上限")
            .replace("%生命值上限", "")
            .split("+")
        )
        calc.set(
            multiplier=Multiplier(hp=scaler),
            fix_value=FixValue(shield=fix_value),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_shield())

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
                    name="甲衣交叠",
                    buff_type="all",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="获取或刷新烈烧佑命护盾叠层，⓪~⑤每层护盾强效+5%",
                        label=labels.get("甲衣交叠", "5"),
                    ),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="烈火攻燔",
                    )
                )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C6",
                    buff_type="all",
                    name="炽烧的至心",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "甲衣交叠":
                    self.buff_T1(buff)
                case "烈火攻燔":
                    self.buff_T2(buff)
                case "炽烧的至心":
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
                name="烈烧佑命之侍护",
                value_type="S",
                dsc="E护盾上限",
                weight=weights.get("烈烧佑命之侍护", 0),
                exclude_buff=ex_buffs.get("烈烧佑命之侍护", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "烈烧佑命之侍护":
                        self.skill_E(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 200,
                    "烈烧佑命之侍护": 10,
                }

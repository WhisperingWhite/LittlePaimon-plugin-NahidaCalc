from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, FixValue, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class Zhongli(Role):
    name = "钟离"

    def buff_T1(self, buff_info: BuffInfo):
        """悬岩宸断"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4", "5"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"{s}层坚璧效果，护盾强效+{s*5}%",
            shield_strength=s * 0.05,
        )

    T2_A_dmg_bonus: float = 0.0
    """T2普攻、重击与下落伤害提高"""
    T2_E_dmg_bonus: float = 0.0
    """T2普攻、重击与下落伤害提高"""
    T2_Q_dmg_bonus: float = 0.0
    """T2普攻、重击与下落伤害提高"""

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """炊金馔玉"""
        self.T2_A_dmg_bonus = prop.hp * 1.39 / 100
        self.T2_E_dmg_bonus = prop.hp * 1.9 / 100
        self.T2_Q_dmg_bonus = prop.hp * 0.33
        buff_info.buff = Buff(
            dsc=f"基于生命上限，普攻、重击与下落基础伤害+{self.T2_A_dmg_bonus}，"
            + f"地心伤害+{self.T2_E_dmg_bonus}，天星伤害+{self.T2_Q_dmg_bonus}",
        )

    def skill_E(self, dmg_info: Dmg):
        """地心"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("地心", self.talents[1].level, "护盾附加吸收量").replace("%", "")
        )
        fix_value = float(
            self.get_scaler("地心", self.talents[1].level, "护盾基础吸收量 ").replace("%", "")
        )
        calc.set(
            multiplier=Multiplier(atk=scaler),
            fix_value=FixValue(shield=fix_value),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_shield())

    def skill_Q(self, dmg_info: Dmg):
        """天星"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("天星", self.talents[2].level, "技能伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="geo",
            multiplier=Multiplier(atk=scaler),
            fix_value=FixValue(dmg=self.T2_Q_dmg_bonus),
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
                    name="悬岩宸断",
                    setting=BuffSetting(
                        dsc="玉璋护盾受到伤害叠层，①~⑤每层护盾强效+5%",
                        label=labels.get("悬岩宸断", "3"),
                    ),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="炊金馔玉",
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "悬岩宸断":
                    self.buff_T1(buff)
                case "炊金馔玉":
                    self.buff_T2(buff)

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
                name="地心",
                value_type="S",
                dsc="玉璋护盾",
                weight=weights.get("地心", 0),
                exclude_buff=ex_buffs.get("地心", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="天星",
                dsc="Q单段",
                weight=weights.get("天星", 0),
                exclude_buff=ex_buffs.get("天星", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "地心":
                        self.skill_E(dmg)
                    case "天星":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 120,
                    "地心": 10,
                    "天星": 10,
                }

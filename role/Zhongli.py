from ..classmodel import (
    Buff,
    BuffInfo,
    BuffSetting,
    Dmg,
    DmgBonus,
    FixValue,
    Multiplier,
)
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

    T2_A_scaler: float = 0.0
    """T2普攻、重击与下落伤害提高"""
    T2_E_scaler: float = 0.0
    """T2普攻、重击与下落伤害提高"""
    T2_Q_scaler: float = 0.0
    """T2普攻、重击与下落伤害提高"""

    def buff_T2(self, buff_info: BuffInfo):
        """炊金馔玉"""
        self.T2_A_scaler = 1.39
        self.T2_E_scaler = 1.9
        self.T2_Q_scaler = 33
        buff_info.buff = Buff(
            dsc=f"普攻、重击与下落倍率+{self.T2_A_scaler}%生命上限，"
            + f"地心伤害+{self.T2_E_scaler}%生命上限，天星伤害+{self.T2_Q_scaler}%生命上限",
        )

    def skill_A(self, dmg_info: Dmg, elem_type="phy"):
        """岩雨"""
        calc = self.create_calc()
        scaler1, scaler2, scaler3, scaler4, scaler5 = [
            float(num.replace("%", "").replace("×4", ""))
            for num in self.get_scaler(
                "普通攻击·岩雨",
                self.talents[0].level,
                "一段伤害",
                "二段伤害",
                "三段伤害",
                "四段伤害",
                "五段伤害",
            )
        ]
        scaler = scaler1 + scaler2 + scaler3 + scaler4 + scaler5 * 4
        calc.set(
            value_type="NA",
            elem_type=elem_type,
            multiplier=Multiplier(atk=scaler, hp=self.T2_A_scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

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

    def buff_E(self, buff_info: BuffInfo):
        """玉璋护盾"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="处于玉璋护盾庇护下,附近敌人全抗-20%",
            resist_reduction=DmgBonus().set({"all": 0.2}),
        )

    def skill_Q(self, dmg_info: Dmg):
        """天星"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("天星", self.talents[2].level, "技能伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="geo",
            multiplier=Multiplier(atk=scaler, hp=self.T2_Q_scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    category: str = "盾辅"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["盾辅", "副C", "武神"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "盾辅":
                return ["生命", "生命%"]
            case "副C":
                return ["攻击%", "生命", "生命%", "岩伤", "暴击", "暴伤", "充能"]
            case "武神":
                return ["攻击", "攻击%", "生命%", "物伤", "暴击", "暴伤"]

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
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="玉璋护盾",
                buff_range="all",
                setting=BuffSetting(label=labels.get("玉璋护盾", "○")),
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
                case "玉璋护盾":
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
                name="岩雨",
                dsc="A一轮普攻前五段",
                weight=weights.get("岩雨", 0),
                exclude_buff=ex_buffs.get("岩雨", []),
            ),
            Dmg(
                index=2,
                source="E",
                name="地心",
                value_type="S",
                dsc="玉璋护盾",
                weight=weights.get("地心", 0),
                exclude_buff=ex_buffs.get("地心", []),
            ),
            Dmg(
                index=3,
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
                    case "岩雨":
                        self.skill_A(dmg)
                    case "地心":
                        self.skill_E(dmg)
                    case "天星":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "盾辅":
                return {
                    "充能效率阈值": 100,
                    "岩雨": 0,
                    "地心": 10,
                    "天星": 0,
                }
            case "副C":
                return {
                    "充能效率阈值": 120,
                    "岩雨": 0,
                    "地心": 10,
                    "天星": 10,
                }
            case "武神":
                return {
                    "充能效率阈值": 100,
                    "岩雨": 10,
                    "地心": 0,
                    "天星": 0,
                }
            case _:
                return {
                    "充能效率阈值": 120,
                    "岩雨": -1,
                    "地心": 10,
                    "天星": 10,
                }

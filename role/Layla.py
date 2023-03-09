from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, FixValue, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class Layla(Role):
    name = "莱依拉"

    def buff_T1(self, buff_info: BuffInfo):
        """如光骤现"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4"]:
                setting.state, s = f"{x}层深眠", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"护盾强效+{s*6}%",
            shield_strength=s * 0.06,
        )

    def buff_T2(self, buff_info: BuffInfo):
        """勿扰沉眠"""
        buff_info.buff = Buff(
            dsc="垂裳端凝之夜发射的飞星倍率+1.5%生命上限",
            target="E",
            multiplier=Multiplier(hp=1.5),
        )

    C1_curtain_shield: float = 1
    """C1护盾吸收量提升"""

    def buff_C1(self, buff_info: BuffInfo):
        """寐领围垣"""
        buff_info.buff = Buff(
            dsc="安眠帷幕护盾吸收量+20%",
        )
        self.C1_curtain_shield = 1.2

    def buff_C4(self, buff_info: BuffInfo, prop: DmgCalc):
        """星示昭明"""
        extra_dmg = prop.hp * 0.05
        buff_info.buff = Buff(
            dsc=f"垂裳端凝之夜发射飞星时，获得「启明」，基于生命上限，全队普攻与重击基础伤害+{extra_dmg}",
            target=["NA", "CA"],
            fix_value=FixValue(dmg=extra_dmg),
        )

    def buff_C6(self, buff_info: BuffInfo):
        """曜光灵炬"""
        buff_info.buff = Buff(
            dsc="垂裳端凝之夜的飞星和星流摇床之梦的星光弹，增伤+40%",
            target=["E", "Q"],
            dmg_bonus=0.4,
        )

    def skill_E(self, dmg_info: Dmg):
        """垂裳端凝之夜"""
        calc = self.create_calc()
        scaler, fix_value = float(
            self.get_scaler("垂裳端凝之夜", self.talents[1].level, "护盾基础吸收量")
            .replace("%生命值上限", "")
            .split("+")
        )
        calc.set(
            value_type="H",
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
                    name="如光骤现",
                    buff_range="all",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="安眠帷幕护盾存在期间，每获得一枚晚星产生深眠效果，每层护盾强效+6%，至多4层",
                        label=labels.get("如光骤现", "4"),
                    ),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="勿扰沉眠",
                    )
                )
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="寐领围垣",
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="星示昭明",
                    )
                )
                if self.info.constellation >= 6:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C6",
                            name="曜光灵炬",
                            buff_range="transbuff",
                        )
                    )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "如光骤现":
                    self.buff_T1(buff)
                case "勿扰沉眠":
                    self.buff_T2(buff)
                case "寐领围垣":
                    self.buff_C1(buff)
                case "星示昭明":
                    self.buff_C4(buff, prop)
                case "曜光灵炬":
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
                name="垂裳端凝之夜",
                value_type="S",
                dsc="E护盾",
                weight=weights.get("垂裳端凝之夜", 0),
                exclude_buff=ex_buffs.get("垂裳端凝之夜", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "垂裳端凝之夜":
                        self.skill_E(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "垂裳端凝之夜": 10,
                }

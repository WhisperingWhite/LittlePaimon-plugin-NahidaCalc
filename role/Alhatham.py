from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, DmgBonus, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class Alhatham(Role):
    name = "艾尔海森"

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """谜林道破"""
        dmg_bonus = min(prop.elem_mastery * 0.1 / 100, 1)
        buff_info.buff = Buff(
            dsc=f"基于每点精通，光幕与殊境·显象缚结增伤+{(dmg_bonus*100):.1f}%",
            target=["E", "Q"],
            dmg_bonus=dmg_bonus,
        )

    def buff_C2(self, buff_info: BuffInfo):
        """辩章"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"产生琢光镜，精通+50，持续8秒（共{s*50}）",
            elem_mastery=s * 50,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """义贯"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["0", "1", "2", "3"]:
                setting.state, s = f"产生{3-x}枚", int(3 - x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"施放殊境·显象缚结15秒内，草伤+{s*10}%",
            elem_dmg_bonus=DmgBonus(dendro=s * 0.1),
        )

    def buff_C4_party(self, buff_info: BuffInfo):
        """义贯(队伍)"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["0", "1", "2", "3"]:
                setting.state, s = f"消耗{x}枚", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"施放殊境·显象缚结15秒内，队友精通+{s*30}%",
            elem_mastery=s * 30,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """正理"""
        buff_info.buff = Buff(
            dsc="琢光镜数量达到上限，暴击+10%，暴伤+70%，持续6秒",
            crit_rate=0.1,
            crit_dmg=0.7,
        )

    def skill_E(self, dmg_info: Dmg):
        """共相·理式摹写"""
        calc = self.create_calc()
        scaler1, scaler2 = float(
            self.get_scaler("共相·理式摹写", self.talents[1].level, "1枚光幕攻击伤害")
            .replace("%攻击力", "")
            .replace("%元素精通", "")
            .split("+")
        )
        calc.set(
            value_type="E",
            elem_type="dendro",
            multiplier=Multiplier(atk=scaler1, em=scaler2),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q(self, dmg_info: Dmg):
        """殊境·显象缚结"""
        calc = self.create_calc()
        scaler1, scaler2 = float(
            self.get_scaler("共相·理式摹写", self.talents[2].level, "单次伤害")
            .replace("%攻击力", "")
            .replace("%元素精通", "")
            .split("+")
        )
        calc.set(
            value_type="Q",
            elem_type="dendro",
            multiplier=Multiplier(atk=scaler1, em=scaler2),
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
                    name="谜林道破",
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="辩章",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="产生琢光镜叠层，①~④每层精通+50",
                        label=labels.get("辩章", "4"),
                    ),
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="义贯",
                        buff_type="propbuff",
                        setting=BuffSetting(
                            dsc="施放殊境·显象缚结时，消耗的琢光镜数量，①~④每枚草伤+10%",
                            label=labels.get("义贯", "4"),
                        ),
                    )
                )
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="义贯(队伍)",
                        buff_type="party",
                        buff_type="propbuff",
                        setting=BuffSetting(
                            label=labels.get("义贯", "4"),
                        ),
                    )
                )
                if self.info.constellation >= 6:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C6",
                            name="正理",
                            buff_type="propbuff",
                        )
                    )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "谜林道破":
                    self.buff_T2(buff)
                case "辩章":
                    self.buff_C2(buff)
                case "义贯":
                    self.buff_C4(buff)
                case "义贯(队伍)":
                    self.buff_C4_party(buff)
                case "正理":
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
                name="共相·理式摹写",
                dsc="E每枚光幕",
                weight=weights.get("共相·理式摹写", 0),
                exclude_buff=ex_buffs.get("共相·理式摹写", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="殊境·显象缚结",
                dsc="Q单段",
                weight=weights.get("殊境·显象缚结", 0),
                exclude_buff=ex_buffs.get("殊境·显象缚结", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "共相·理式摹写":
                        self.skill_E(dmg)
                    case "殊境·显象缚结":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 120,
                    "共相·理式摹写": 10,
                    "殊境·显象缚结": 10,
                }

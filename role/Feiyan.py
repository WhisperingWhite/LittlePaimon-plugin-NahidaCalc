from ..classmodel import Dmg, Buff, BuffInfo, BuffSetting, DmgBonus, Multiplier
from ._model import Role


class Feiyan(Role):
    name = "烟绯"

    def buff_T1(self, buff_info: BuffInfo):
        """关联条款"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4"]:
                setting.state, s = f"{x}枚", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"消耗丹火印，火伤+{5*s}%，持续6s",
            elem_dmg_bonus=DmgBonus(pyro=0.05 * s),
        )

    def buff_C2(self, buff_info: BuffInfo):
        """最终解释权"""
        buff_info.buff = Buff(
            dsc="生命低于一半的敌方，重击暴击+20%",
            crit_rate=0.2,
        )

    def skill_A(self, dmg_info: Dmg, reaction=""):
        """火漆制印"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("普通攻击·火漆制印", self.talents[0].level, "重击伤害").replace("%", "")
        )
        calc.set(
            value_type="CA",
            elem_type="pyro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_Q(self, buff_info: BuffInfo):
        """凭此结契·灼灼"""
        dmg_bonus = float(
            self.get_scaler("凭此结契", self.talents[2].level, "重击伤害提升").replace("%", "")
        )
        buff_info.buff = Buff(
            dsc=f"施放凭此结契，重击增伤+{dmg_bonus}%",
            target="CA",
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
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="关联条款",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="消耗丹火印，⓪~④每枚火伤+5%",
                        label=labels.get("关联条款", "4"),
                    ),
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="最终解释权",
                )
            )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="凭此结契·灼灼",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "关联条款":
                    self.buff_T1(buff)
                case "最终解释权":
                    self.buff_C2(buff)
                case "凭此结契·灼灼":
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
                source="A",
                name="火漆制印",
                dsc="A重击",
                weight=weights.get("火漆制印", 0),
                exclude_buff=ex_buffs.get("火漆制印", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "火漆制印":
                        self.skill_A(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "火漆制印": 10,
                }

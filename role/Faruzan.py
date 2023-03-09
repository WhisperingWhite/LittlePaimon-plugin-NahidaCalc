from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, FixValue, Multiplier
from ._model import Role


class Faruzan(Role):
    name = "珐露珊"

    def buff_T2(self, buff_info: BuffInfo):
        """七窟遗智"""
        base_dmg = self.prop.atk_base * 0.32
        buff_info.buff = Buff(
            dsc=f"祈风之赐效果下，造成风伤时获得烈风护持：基于珐露珊基础攻击，基础伤害+{int(base_dmg)}",
            fix_value=FixValue(dmg=base_dmg),
        )

    def buff_C6(self, buff_info: BuffInfo):
        """妙道合真"""
        buff_info.buff = Buff(
            dsc="祈风之赐效果下，风伤暴伤+40%",
            crit_dmg=0.4,
        )

    def buff_Q1(self, buff_info: BuffInfo):
        """抟风秘道·祈风之赐"""
        dmg_bonus = float(
            self.get_scaler("抟风秘道", self.talents[2].level, "风元素伤害加成").replace("%", "")
        )
        buff_info.buff = Buff(
            dsc=f"烈风波释放时，全队风伤+{dmg_bonus}%",
            elem_dmg_bonus=DmgBonus(anemo=dmg_bonus / 100),
        )

    def buff_Q2(self, buff_info: BuffInfo):
        """抟风秘道·诡风之祸"""
        buff_info.buff = Buff(
            dsc="烈风波释放时，风抗-30%",
            resist_reduction=DmgBonus(anemo=0.3),
        )

    def skill_Q(self, dmg_info: Dmg):
        """抟风秘道"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("抟风秘道", self.talents[2].level, "技能伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="anemo",
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
                    name="七窟遗智",
                )
            )
        # 命座
        if self.info.constellation >= 6:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C6",
                    name="妙道合真",
                    buff_range="all",
                )
            )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="抟风秘道·祈风之赐",
                buff_range="all",
                buff_type="propbuff",
            )
        )
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="抟风秘道·诡风之祸",
                buff_range="all",
            )
        )

        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "七窟遗智":
                    self.buff_T2(buff)
                case "妙道合真":
                    self.buff_C6(buff)
                case "抟风秘道·祈风之赐":
                    self.buff_Q1(buff)
                case "抟风秘道·诡风之祸":
                    self.buff_Q2(buff)

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
                name="抟风秘道",
                dsc="Q烈风波每段",
                weight=weights.get("抟风秘道", 0),
                exclude_buff=ex_buffs.get("抟风秘道", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "抟风秘道":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "抟风秘道": 10,
                }

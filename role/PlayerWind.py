from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, DmgBonus, Multiplier
from ._model import Role


class PlayerWind(Role):
    name = "风主"

    def buff_C6(self, buff_info: BuffInfo):
        """纠缠的信风"""
        setting = buff_info.setting
        buff_info.buff = Buff(
            dsc="风息激荡命中，风抗-20%",
            resist_reduction=DmgBonus(anemo=0.2),
        )
        match setting.label:
            case x if x in ["火", "水", "雷", "冰"]:
                setting.state = f"{x}风"
                buff_info.buff.dsc += f"，{x}抗-20%"
                buff_info.buff.resist_reduction.set({x: 0.2})

    def skill_Q(self, dmg_info: Dmg):
        """风息激荡"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("风息激荡", self.talents[2].level, "龙卷风伤害").replace(
                "%", ""
            )
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
        # 命座
        if self.info.constellation >= 6:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C6",
                    name="纠缠的信风",
                    buff_range="all",
                    setting=BuffSetting(
                        dsc="元素转化（火，水，雷，冰）：对应抗性-20%",
                        label=labels.get("纠缠的信风", "火"),
                    ),
                )
            )

        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "纠缠的信风":
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
                source="Q",
                name="风息激荡",
                dsc="龙卷风风伤每段",
                weight=weights.get("风息激荡", 0),
                exclude_buff=ex_buffs.get("风息激荡", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "风息激荡":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 180,
                    "风息激荡": 10,
                }

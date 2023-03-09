from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, FixValue, Multiplier
from ._model import Role


class Diona(Role):
    name = "迪奥娜"

    C2_absorb: float = 1
    """猫爪护盾吸收倍率"""

    def buff_C2(self, buff_info: BuffInfo):
        """猫爪冰摇"""
        self.absorb = 1.15
        buff_info.buff = Buff(
            dsc="猫爪冻冻增伤+15%，护盾的吸收量+15%",
            target="E",
            dmg_bonus=0.15,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """猫尾打烊之时"""
        setting = buff_info.setting
        match setting.label:
            case "1":
                setting.state = "生命值低于50%"
                buff_info.buff.dsc = "受治疗+30%"
                buff_info.buff.healing = 0.3
            case "2":
                setting.state = "生命值高于50%"
                buff_info.buff.dsc = "精通+200"
                buff_info.buff.elem_mastery = 200
            case _:
                setting.state = "×"

    def skill_E(self, dmg_info: Dmg):
        """猫爪冻冻"""
        calc = self.create_calc()
        scaler, fix_value = float(
            self.get_scaler("降众天华", self.talents[1].level, "护盾基础吸收量")
            .replace("%最大生命值", "")
            .split("+")
        )
        calc.set(
            value_type="S",
            multiplier=Multiplier(hp=scaler),
            fix_value=FixValue(shield=fix_value),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_shield() * self.C2_absorb)

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="猫爪冰摇",
                )
            )
            if self.info.constellation >= 6:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C6",
                        name="猫尾打烊之时",
                        buff_range="active",
                        buff_range="propbuff",
                        setting=BuffSetting(
                            dsc="最烈特调领域内，①生命值低于50%：受治疗+30%；②生命值高于50%：精通+200",
                            label=labels.get("猫尾打烊之时", "2"),
                        ),
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "猫爪冰摇":
                    self.buff_C2(buff)
                case "猫尾打烊之时":
                    self.buff_C6(buff, prop)

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
                name="猫爪冻冻",
                value_type="S",
                dsc="猫爪护盾",
                weight=weights.get("猫爪冻冻", 0),
                exclude_buff=ex_buffs.get("猫爪冻冻", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "猫爪冻冻":
                        self.skill_E(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 160,
                    "猫爪冻冻": 10,
                }

from ..classmodel import Buff, BuffInfo, Dmg, Multiplier, PoFValue
from ._model import Role


class Sara(Role):
    name = "裟罗"

    def buff_C6(self, buff_info: BuffInfo):
        """我界"""
        buff_info.buff = Buff(
            dsc="「乌羽」提升效果状态下，雷伤暴伤+60%",
            crit_dmg=0.6,
        )

    def skill_Q(self, dmg_info: Dmg):
        """煌煌千道镇式"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("煌煌千道镇式", self.talents[2].level, "天狗咒雷•金刚坏伤害").replace(
                "%", ""
            )
        )
        calc.set(
            value_type="Q",
            elem_type="electro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_E(self, buff_info: BuffInfo):
        """鸦羽天狗霆雷召咒·乌羽"""
        scaler = float(
            self.get_scaler("鸦羽天狗霆雷召咒", self.talents[1].level, "攻击力加成比例").replace(
                "%", ""
            )
        )
        atk = self.prop.atk_base * scaler / 100
        buff_info.buff = Buff(
            dsc=f"「乌羽」引发的天狗咒雷命中6秒内，场上角色攻击+{atk:.0f}",
            atk=PoFValue(fix=atk),
        )

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
                    name="我界",
                )
            )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="鸦羽天狗霆雷召咒·乌羽",
                buff_type="propbuff",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "我界":
                    self.buff_C6(buff)
                case "鸦羽天狗霆雷召咒·乌羽":
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
                source="Q",
                name="煌煌千道镇式",
                dsc="Q天狗咒雷•金刚坏",
                weight=weights.get("煌煌千道镇式", 0),
                exclude_buff=ex_buffs.get("煌煌千道镇式", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "煌煌千道镇式":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 200,
                    "煌煌千道镇式": 10,
                }

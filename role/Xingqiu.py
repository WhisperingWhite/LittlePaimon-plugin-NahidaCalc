from ..classmodel import Dmg, Buff, BuffInfo, Multiplier
from ._model import Role


class Xingqiu(Role):
    name = "行秋"

    def buff_C2(self, buff_info: BuffInfo):
        """天青现虹"""
        buff_info.buff = Buff(
            dsc="剑雨攻击的敌人4秒内，水抗-15%",
            dmg_bonus=0.4,
        )

    C4_rainscreen: float = 1.0

    def buff_C4(self, buff_info: BuffInfo):
        """孤舟斩蛟"""
        buff_info.buff = Buff(
            dsc="古华剑·裁雨留虹持续期间，古华剑·画雨笼山倍率*1.5",
        )
        self.C4_rainscreen = 1.5

    def skill_E(self, dmg_info: Dmg):
        """古华剑·画雨笼山"""
        calc = self.create_calc()
        scaler = sum(
            float(
                self.get_scaler("古华剑·画雨笼山", self.talents[1].level, "技能伤害")
                .replace("%", "")
                .split("+")
            )
        )
        calc.set(
            value_type="E",
            elem_type="hydro",
            multiplier=Multiplier(atk=scaler * self.C4_rainscreen),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q(self, dmg_info: Dmg):
        """古华剑·裁雨留虹"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("古华剑·裁雨留虹", self.talents[2].level, "剑雨伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="hydro",
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
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="天青现虹",
                    buff_range="all",
                )
            )
            if self.info.constellation >= 2:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="孤舟斩蛟",
                        buff_type="propbuff",
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "天青现虹":
                    self.buff_C2(buff)
                case "孤舟斩蛟":
                    self.buff_C4(buff)

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
                name="古华剑·画雨笼山",
                dsc="E两段",
                weight=weights.get("古华剑·画雨笼山", 0),
                exclude_buff=ex_buffs.get("古华剑·画雨笼山", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="古华剑·裁雨留虹",
                dsc="Q剑雨每段",
                weight=weights.get("古华剑·裁雨留虹", 0),
                exclude_buff=ex_buffs.get("古华剑·裁雨留虹", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "古华剑·画雨笼山":
                        self.skill_E(dmg)
                    case "古华剑·裁雨留虹":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "古华剑·画雨笼山": 5,
                    "古华剑·裁雨留虹": 10,
                }

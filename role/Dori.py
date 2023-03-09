from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, Multiplier
from ._model import Role


class Dori(Role):
    name = "多莉"

    def buff_C4(self, buff_info: BuffInfo):
        """酌盈剂虚"""
        setting = buff_info.setting
        healing, recharge = 0, 0
        match setting.label:
            case "10":
                setting.state, healing = "受治疗提升", 50
            case "01":
                setting.state, recharge = "充能提升", 30
            case "11":
                setting.state, healing, recharge = "受治疗、充能提升", 50, 30
            case _:
                (setting.state,) = "×", 0
        buff_info.buff = Buff(
            dsc=f"与灯中幽精相连，受治疗+{healing*100}%，充能+{recharge}%",
            healing=healing,
            recharge=recharge,
        )

    def skill_Q(self, dmg_info: Dmg):
        """卡萨扎莱宫的无微不至"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("卡萨扎莱宫的无微不至", self.talents[2].level, "持续治疗量")
            .replace("%生命值上限", "")
            .split("+")
        )
        calc.set(
            value_type="H",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_healing())

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 命座
        if self.info.constellation >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C4",
                    name="酌盈剂虚",
                    buff_range="active",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="角色与灯中幽精相连，依据生命值与能量，"
                        + "'10'：生命低于50%，受治疗+50%；'01'：能量低于50%，充能+30%",
                        label=labels.get("酌盈剂虚", "11"),
                    ),
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "酌盈剂虚":
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
                source="Q",
                name="卡萨扎莱宫的无微不至",
                dsc="Q治疗每跳",
                weight=weights.get("卡萨扎莱宫的无微不至", 0),
                exclude_buff=ex_buffs.get("卡萨扎莱宫的无微不至", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "卡萨扎莱宫的无微不至":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 240,
                    "卡萨扎莱宫的无微不至": 10,
                }

from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, Multiplier
from ._model import Role


class Beidou(Role):
    name = "北斗"

    def buff_T2(self, buff_info: BuffInfo):
        """霹雳连霄"""
        buff_info.buff = Buff(
            dsc="捉浪弹反10秒内，普攻与重击增伤+15%",
            target=["NA", "CA"],
            dmg_bonus=0.15,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """北斗祓幽孽"""
        buff_info.buff = Buff(
            dsc="斫雷持续期间，雷抗-15%",
            resist_reduction=DmgBonus(electro=0.15),
        )

    def skill_Q(self, dmg_info: Dmg):
        """斫雷"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("斫雷", self.talents[2].level, "闪电伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="electro",
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
                    name="霹雳连霄",
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C6",
                    name="北斗祓幽孽",
                    buff_range="all",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "霹雳连霄":
                    self.buff_T2(buff)
                case "北斗祓幽孽":
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
                name="斫雷",
                dsc="Q闪雷",
                weight=weights.get("斫雷", 0),
                exclude_buff=ex_buffs.get("斫雷", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "斫雷":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 200,
                    "斫雷": 10,
                }

from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, Multiplier
from ._model import Role


class Ningguang(Role):
    name = "凝光"

    def buff_T2(self, buff_info: BuffInfo):
        """储之千日，用之一刻"""
        buff_info.buff = Buff(
            dsc="穿过璇玑屏，岩伤+12%",
            elem_dmg_bonus=DmgBonus(geo=0.12),
        )

    def skill_Q(self, dmg_info: Dmg):
        """天权崩玉"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("天权崩玉", self.talents[2].level, "荒泷逆袈裟连斩伤害")
            .replace("%", "")
            .replace("每个", ""),
        )
        calc.set(
            value_type="Q",
            elem_type="geo",
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
                    name="储之千日，用之一刻",
                    buff_range="all",
                    buff_type="propbuff",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "储之千日，用之一刻":
                    self.buff_T2(buff)

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
                name="天权崩玉",
                dsc="Q每颗宝石",
                weight=weights.get("天权崩玉", 0),
                exclude_buff=ex_buffs.get("天权崩玉", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "天权崩玉":
                        self.skill_Q(dmg)

        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "天权崩玉": 10,
                }

from ..classmodel import Dmg, BuffInfo, Multiplier
from ._model import Role


class Tartaglia(Role):
    name = "达达利亚"

    def skill_Q(self, dmg_info: Dmg):
        """极恶技·尽灭闪·尽灭水光"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("极恶技·尽灭闪", self.talents[2].level, "技能伤害·远程").replace(
                "%", ""
            )
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
        return []

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""

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
                name="极恶技·尽灭闪·尽灭水光",
                dsc="Q远程",
                weight=weights.get("极恶技·尽灭闪·尽灭水光", 0),
                exclude_buff=ex_buffs.get("极恶技·尽灭闪·尽灭水光", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "极恶技·尽灭闪·尽灭水光":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 120,
                    "极恶技·尽灭闪·尽灭水光": 10,
                }

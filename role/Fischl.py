from ..classmodel import Buff, BuffInfo, Dmg, Multiplier
from ._model import Role


class Fischl(Role):
    name = "菲谢尔"

    def skill_E(self, dmg_info: Dmg, reaction=""):
        """夜巡影翼-激化"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("夜巡影翼-激化", self.talents[1].level, "奥兹攻击伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="electro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_Q(self, buff_info: BuffInfo):
        """圣仪·煟煌随狼行·启途誓使"""
        buff_info.buff = Buff(
            dsc="启途誓使状态下，精通+100",
            elem_mastery=100,
        )

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
                source="E",
                name="夜巡影翼-激化",
                dsc="E奥兹魔弹每发",
                weight=weights.get("夜巡影翼-激化", 0),
                exclude_buff=ex_buffs.get("夜巡影翼-激化", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "夜巡影翼-激化":
                        self.skill_E(dmg, "激化")
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case _:
                return {
                    "充能效率阈值": 100,
                    "夜巡影翼-激化": 10,
                }

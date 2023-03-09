from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, Multiplier
from ._model import Role


class Chongyun(Role):
    name = "重云"

    def buff_T2(self, buff_info: BuffInfo):
        """追冰剑诀"""
        buff_info.buff = Buff(
            dsc="被灵刃击中的敌人，冰抗-10%，持续8秒",
            resist_reduction=DmgBonus(cryo=0.1),
        )

    def buff_C6(self, buff_info: BuffInfo):
        """四灵捧圣"""
        buff_info.buff = Buff(
            dsc="对生命百分比低于重云的敌人，灵刃·云开星落增伤+15%",
            target="Q",
            dmg_bonus=0.15,
        )

    def skill_Q(self, dmg_info: Dmg):
        """灵刃·云开星落"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("灵刃·云开星落", self.talents[2].level, "技能伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="cryo",
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
                    name="追冰剑诀",
                    buff_range="all",
                )
            )
        # 命座
        if self.info.constellation >= 6:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C6",
                    name="四灵捧圣",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "追冰剑诀":
                    self.buff_T2(buff)
                case "四灵捧圣":
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
                name="灵刃·云开星落",
                dsc="Q灵刃每柄",
                weight=weights.get("灵刃·云开星落", 0),
                exclude_buff=ex_buffs.get("灵刃·云开星落", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "灵刃·云开星落":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 120,
                    "灵刃·云开星落": 10,
                }

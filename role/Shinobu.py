from ..classmodel import Buff, BuffInfo, Dmg, Multiplier, FixValue
from ._model import Role


class Shinobu(Role):
    name = "忍"

    def buff_T1(self, buff_info: BuffInfo):
        """破笼之志"""
        buff_info.buff = Buff(
            dsc="生命值低于50%时，治疗+15%",
            healing=0.15,
        )

    T2_ring_healing: int = 0
    """T2越祓雷草之轮治疗倍率"""
    T2_ring_dmg: int = 0
    """T2越祓雷草之轮伤害倍率"""

    def buff_T2(self, buff_info: BuffInfo):
        """安心之所"""
        self.T2_ring_healing = 75
        self.T2_ring_dmg = 25
        buff_info.buff = Buff(
            dsc="越祓雷草之轮治疗倍率+75%精通，伤害倍率+25%精通",
        )

    def buff_C6(self, buff_info: BuffInfo):
        """割舍软弱之心"""
        buff_info.buff = Buff(
            dsc="久岐忍生命降至25%以下时，精通+150，持续15秒",
            elem_mastery=150,
        )

    def skill_E(self, dmg_info: Dmg):
        """越祓雷草之轮"""
        calc = self.create_calc()
        scaler1, scaler2 = float(
            self.get_scaler("越祓雷草之轮", self.talents[1].level, "越祓草轮治疗量")
            .replace("%生命值上限", "")
            .split("+")
        )
        calc.set(
            value_type="H",
            multiplier=Multiplier(hp=scaler1, em=self.T2_ring_healing),
            fix_value=FixValue(heal=scaler2),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_healing())

    def hyperbloom(self, dmg_info: Dmg):
        """超绽放"""
        calc = self.create_calc()
        calc.set(
            reaction_type="超绽放",
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_trans_reac_dmg())

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="破笼之志",
                    buff_type="propbuff",
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="安心之所",
                    )
                )
        # 命座
        if self.info.constellation >= 6:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C6",
                    name="割舍软弱之心",
                    buff_type="propbuff",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "破笼之志":
                    self.buff_T1(buff)
                case "安心之所":
                    self.buff_T2(buff)
                case "割舍软弱之心":
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
                source="E",
                name="越祓雷草之轮",
                dsc="E草轮每跳治疗",
                weight=weights.get("越祓雷草之轮", 0),
                exclude_buff=ex_buffs.get("越祓雷草之轮", []),
            ),
            Dmg(
                index=2,
                name="超绽放",
                dsc="每枚种子",
                weight=weights.get("超绽放", 0),
                exclude_buff=ex_buffs.get("超绽放", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "越祓雷草之轮":
                        self.skill_E(dmg)
                    case "超绽放":
                        self.hyperbloom(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "越祓雷草之轮": 10,
                    "超绽放": 10,
                }

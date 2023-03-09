from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, Multiplier, PoFValue
from ..dmg_calc import DmgCalc
from ._model import Role


class Xiangling(Role):
    name = "香菱"

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """绝云朝天椒"""
        buff_info.buff = Buff(
            dsc=f"拾取辣椒10秒内,攻击+10%(+{prop.atk_base*0.1})",
            atk=PoFValue(percent=0.1),
        )

    def buff_C1(self, buff_info: BuffInfo):
        """外酥里嫩"""
        buff_info.buff = Buff(
            dsc="锅巴命中6秒内,火抗-15%",
            resist_reduction=DmgBonus(pyro=0.15),
        )

    def buff_C6(self, buff_info: BuffInfo):
        """大龙卷旋火轮"""
        buff_info.buff = Buff(
            dsc="旋火轮持续期间，全队火伤+15%",
            elem_dmg_bonus=DmgBonus(pyro=0.15),
        )

    def skill_Q(self, dmg_info: Dmg, reaction=""):
        """旋火轮"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("旋火轮", self.talents[2].level, "旋火轮伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="pyro",
            reaction_type=reaction,
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
                    name="绝云朝天椒",
                    buff_range="all",
                    buff_type="propbuff",
                )
            )
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="外酥里嫩",
                    buff_range="all",
                )
            )
            if self.info.constellation >= 6:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C6",
                        name="大龙卷旋火轮",
                        buff_range="all",
                        buff_type="propbuff",
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "绝云朝天椒":
                    self.buff_T2(buff, prop)
                case "外酥里嫩":
                    self.buff_C1(buff)
                case "大龙卷旋火轮":
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
                name="旋火轮",
                dsc="Q每转",
                weight=weights.get("旋火轮", 0),
                exclude_buff=ex_buffs.get("旋火轮", ["大龙卷旋火轮"]),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "旋火轮-蒸发":
                        self.skill_Q(dmg, "蒸发")
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 230,
                    "旋火轮-蒸发": 10,
                }

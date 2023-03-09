from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, FixValue, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class Yaoyao(Role):
    name = "柯莱"

    def buff_C1(self, buff_info: BuffInfo):
        """妙受琼阁"""
        buff_info.buff = Buff(
            dsc="白玉萝卜炸裂时，场上角色草伤害+15%",
            elem_dmg_bonus=DmgBonus(dendro=0.15),
        )

    def buff_C4(self, buff_info: BuffInfo, prop: DmgCalc):
        """爰爰可亲"""
        elem_ma = prop.hp * 0.3 / 100
        buff_info.buff = Buff(
            dsc=f"施放云台团团降芦菔或玉颗珊珊月中落8秒内，基于生命上限，精通+{elem_ma}",
            elem_mastery=elem_ma,
        )

    def skill_Q(self, dmg_info: Dmg):
        """玉颗珊珊月中落"""
        calc = self.create_calc()
        scaler, fix_value = float(
            self.get_scaler("玉颗珊珊月中落", self.talents[2].level, "桂子仙机白玉萝卜治疗量")
            .replace("%生命值上限", "")
            .split("+")
        )
        calc.set(
            multiplier=Multiplier(atk=scaler),
            fix_value=FixValue(heal=fix_value),
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
        if self.info.ascension >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="妙受琼阁",
                    buff_range="active",
                    buff_type="propbuff",
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="爰爰可亲",
                        buff_type="transbuff",
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "妙受琼阁":
                    self.buff_C1(buff)
                case "爰爰可亲":
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
                name="玉颗珊珊月中落",
                value_type="H",
                dsc="Q萝卜治疗每跳",
                weight=weights.get("玉颗珊珊月中落", 0),
                exclude_buff=ex_buffs.get("玉颗珊珊月中落", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "玉颗珊珊月中落":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 200,
                    "玉颗珊珊月中落": 10,
                }

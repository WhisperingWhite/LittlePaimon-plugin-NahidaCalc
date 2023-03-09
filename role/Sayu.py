from ..classmodel import Buff, BuffInfo, Dmg, FixValue, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class Sayu(Role):
    name = "早柚"

    def buff_C2(self, buff_info: BuffInfo):
        """理清逃跑路线"""
        buff_info.buff = Buff(
            dsc="长按风风轮，风风轮舞踢最大增伤+66%",
            target="E",
            dmg_bonus=0.66,
        )

    C6_daruma_healing: float = 0.0

    def buff_C6(self, buff_info: BuffInfo, prop: DmgCalc):
        """呼呼大睡时间"""
        healing = min(prop.elem_mastery * 3, 6000)
        buff_info.buff = Buff(
            dsc=f"不倒貉貉回复量+{healing}",
        )
        self.C6_daruma_healing = healing

    def skill_Q(self, dmg_info: Dmg):
        """呜呼流·影貉缭乱"""
        calc = self.create_calc()
        scaler, fix_value = float(
            self.get_scaler("呜呼流·影貉缭乱", self.talents[2].level, "不倒貉貉治疗量")
            .replace("%攻击力", "")
            .split("+")
        )
        calc.set(
            multiplier=Multiplier(atk=scaler),
            fix_value=FixValue(heal=fix_value + self.C6_daruma_healing),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_healing())

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []

        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="理清逃跑路线",
                )
            )
            if self.info.constellation >= 6:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C6",
                        name="呼呼大睡时间",
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "理清逃跑路线":
                    self.buff_C2(buff)
                case "呼呼大睡时间":
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
                name="呜呼流·影貉缭乱",
                value_type="H",
                dsc="Q不倒貉貉治疗",
                weight=weights.get("呜呼流·影貉缭乱", 0),
                exclude_buff=ex_buffs.get("呜呼流·影貉缭乱", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "呜呼流·影貉缭乱":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 200,
                    "呜呼流·影貉缭乱": 10,
                }

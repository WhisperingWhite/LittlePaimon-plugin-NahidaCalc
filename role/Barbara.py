from ..classmodel import Dmg, Buff, BuffInfo, DmgBonus, Multiplier, FixValue
from ._model import Role


class Barbara(Role):
    name = "芭芭拉"

    def buff_T1(self, buff_info: BuffInfo):
        buff_info.buff = Buff(
            dsc="演唱，开始♪持续期间,场上角色水伤+15%",
            elem_dmg_bonus=DmgBonus(hydro=0.15),
        )

    def skill_Q(self, dmg_info: Dmg):
        """闪耀奇迹♪"""
        calc = self.create_calc()
        scaler, fix_value = float(
            self.get_scaler("闪耀奇迹♪", self.talents[2].level, "治疗量")
            .replace("%生命值上限", "")
            .split("+")
        )
        calc.set(
            multiplier=Multiplier(hp=scaler),
            fix_value=FixValue(heal=fix_value),
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
                    source=f"{self.name}-T1",
                    name="元气迸发",
                    buff_range="active",
                    buff_type="propbuff",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "元气迸发":
                    self.buff_T1(buff)

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
                name="闪耀奇迹♪",
                value_type="H",
                dsc="Q治疗",
                weight=weights.get("闪耀奇迹♪", 0),
                exclude_buff=ex_buffs.get("闪耀奇迹♪", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "闪耀奇迹♪":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:

        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 150,
                    "闪耀奇迹♪": 10,
                }

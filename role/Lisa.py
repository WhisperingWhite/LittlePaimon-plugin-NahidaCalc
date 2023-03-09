from ..classmodel import Dmg, Buff, BuffInfo, Multiplier
from ._model import Role


class Lisa(Role):
    name = "丽莎"

    def buff_T2(self, buff_info: BuffInfo):
        """静电场力"""
        buff_info.buff = Buff(
            dsc="蔷薇的雷光命中10秒内，减防+15%",
            def_reduction=0.15,
        )

    def skill_Q(self, dmg_info: Dmg):
        """蔷薇的雷光"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("蔷薇的雷光", self.talents[2].level, "雷光放电伤害").replace("%", "")
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

    def setting(self, labels: dict) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T2",
                    name="静电场力",
                    buff_range="all",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "静电场力":
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
                name="蔷薇的雷光",
                dsc="Q每段雷光",
                weight=weights.get("蔷薇的雷光", 0),
                exclude_buff=ex_buffs.get("蔷薇的雷光", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "蔷薇的雷光":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 230,
                    "蔷薇的雷光": 10,
                }

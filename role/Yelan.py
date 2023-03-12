from ..classmodel import Dmg, Buff, BuffInfo, BuffSetting, Multiplier, PoFValue
from ._model import Role
from ..dmg_calc import DmgCalc


class Yelan(Role):
    name = "夜兰"

    def buff_T1(self, buff_info: BuffInfo):
        """猜先有方"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4"]:
                setting.state, s = f"{x}种", int(x)
            case _:
                setting.state, s = "×", 0
        hp_per = 0.3 if s == 4 else s * 0.06
        buff_info.buff = Buff(
            dsc=f"队伍中存在{s}种元素，生命上限+{hp_per*100}%({self.prop.hp_base*hp_per:.0f})",
            hp=PoFValue(percent=hp_per),
        )

    def buff_T2(self, buff_info: BuffInfo):
        """妙转随心"""
        setting = buff_info.setting
        match setting.label:
            case x if x in [
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "11",
                "12",
                "13",
                "14",
                "15",
            ]:
                setting.state, s = f"{x}秒", int(x)
            case _:
                setting.state, s = "×", 0
        dmg_bonus = min(s * 0.035, 50)
        buff_info.buff = Buff(
            dsc=f"玄掷玲珑存在期间，场上角色增伤+{dmg_bonus*100:.1f}%",
            dmg_bonus=dmg_bonus,
        )

    def buff_C4(self, buff_info: BuffInfo, prop: DmgCalc):
        """诓惑者，接树移花"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4"]:
                setting.state, s = f"{x}次", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"络命丝标记爆发{s}次，全队生命值上限+{s*10}%({prop.hp_base*s*0.1}),持续25秒",
            hp=PoFValue(percent=s * 0.1),
        )

    def skill_Q(self, dmg_info: Dmg):
        """渊图玲珑骰"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("渊图玲珑骰", self.talents[2].level, "玄掷玲珑伤害").replace(
                "%生命值上限*3", ""
            )
        )
        calc.set(
            value_type="Q",
            elem_type="hydro",
            multiplier=Multiplier(hp=scaler),
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
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="猜先有方",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="队伍角色的元素类型，①~④种分别生命值上限+6%/12%/18%/30%",
                        label=labels.get("猜先有方", "3"),
                    ),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="妙转随心",
                        buff_range="active",
                        setting=BuffSetting(
                            dsc="玄掷玲珑存在期间，每秒叠层，⓪~⑮每层场上角色增伤+3.5%",
                            label=labels.get("妙转随心", "6"),
                        ),
                    )
                )
            # 命座
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="诓惑者，接树移花",
                        buff_range="all",
                        buff_type="propbuff",
                        setting=BuffSetting(
                            dsc="络命丝标记爆发，⓪~④每次全队生命值上限+10%",
                            label=labels.get("诓惑者，接树移花", "4"),
                        ),
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "猜先有方":
                    self.buff_T1(buff)
                case "妙转随心":
                    self.buff_T2(buff)
                case "诓惑者，接树移花":
                    self.buff_C4(buff, prop)

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
                name="渊图玲珑骰",
                dsc="Q玄掷玲珑每段",
                weight=weights.get("渊图玲珑骰", 0),
                exclude_buff=ex_buffs.get("渊图玲珑骰", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "渊图玲珑骰":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 180,
                    "渊图玲珑骰": 10,
                }

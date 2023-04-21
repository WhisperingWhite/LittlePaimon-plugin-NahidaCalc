from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, DmgBonus, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class Yae(Role):
    name = "神子"

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """启蜇之祝词"""
        dmg_bonus = prop.elem_mastery * 0.15 / 100
        buff_info.buff = Buff(
            dsc=f"基于精通，杀生樱增伤+{dmg_bonus*100:.1f}%",
            target="E",
            dmg_bonus=dmg_bonus,
        )

    sakura_rank: int = 3
    """杀生樱最大位阶"""

    def buff_C2(self, buff_info: BuffInfo):
        """望月吼哕声"""
        self.sakura_rank = 4
        buff_info.buff = Buff(
            dsc="杀生樱位阶上限提升至肆阶",
        )

    def buff_C4(self, buff_info: BuffInfo):
        """绯樱引雷章"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="杀生樱命中5秒内，全队雷伤+20%",
            elem_dmg_bonus=DmgBonus(electro=0.2),
        )

    def buff_C6(self, buff_info: BuffInfo):
        """大杀生咒禁"""
        buff_info.buff = Buff(
            dsc="杀生樱无视防御+60%",
            target="E",
            def_piercing=0.6,
        )

    def skill_E(self, dmg_info: Dmg, reaction=""):
        """野干役咒·杀生樱"""
        calc = self.create_calc()
        scaler1, scaler2 = [
            float(i.replace("%", ""))
            for i in self.get_scaler(
                "野干役咒·杀生樱",
                self.talents[1].level,
                "杀生樱伤害·叁阶",
                "杀生樱伤害·肆阶",
            )
        ]
        scaler = scaler1 if self.sakura_rank == 3 else scaler2
        calc.set(
            value_type="E",
            elem_type="electro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_Q(self, dmg_info: Dmg, reaction=""):
        """大密法·天狐显真"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("大密法·天狐显真", self.talents[2].level, "天狐霆雷伤害").replace(
                "%", ""
            )
        )
        calc.set(
            value_type="Q",
            elem_type="electro",
            reaction_type=reaction,
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    category: str = "激化狐"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["激化狐", "纯雷狐"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "激化狐":
                return ["攻击", "攻击%", "雷伤", "暴击", "暴伤", "精通", "充能"]
            case "纯雷狐":
                return ["攻击", "攻击%", "雷伤", "暴击", "暴伤", "精通", "充能"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T2",
                    name="启蜇之祝词",
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="望月吼哕声",
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="绯樱引雷章",
                        buff_range="all",
                        buff_type="propbuff",
                        setting=BuffSetting(label=labels.get("绯樱引雷章", "○")),
                    )
                )
                if self.info.constellation >= 6:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C6",
                            name="大杀生咒禁",
                        )
                    )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "启蜇之祝词":
                    self.buff_T2(buff, prop)
                case "望月吼哕声":
                    self.buff_C2(buff)
                case "绯樱引雷章":
                    self.buff_C4(buff)
                case "大杀生咒禁":
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
                name="野干役咒·杀生樱",
                dsc="E杀生樱每段",
                weight=weights.get("野干役咒·杀生樱", 0),
                exclude_buff=ex_buffs.get("野干役咒·杀生樱", []),
            ),
            Dmg(
                index=2,
                source="E",
                name="野干役咒·杀生樱-激化",
                dsc="E杀生樱每段激化",
                weight=weights.get("野干役咒·杀生樱-激化", 0),
                exclude_buff=ex_buffs.get("野干役咒·杀生樱-激化", []),
            ),
            Dmg(
                index=3,
                source="Q",
                name="大密法·天狐显真",
                dsc="Q天狐霆雷",
                weight=weights.get("大密法·天狐显真", 0),
                exclude_buff=ex_buffs.get("大密法·天狐显真", []),
            ),
            Dmg(
                index=4,
                source="E",
                name="大密法·天狐显真-激化",
                dsc="Q天狐霆雷激化",
                weight=weights.get("大密法·天狐显真-激化", 0),
                exclude_buff=ex_buffs.get("大密法·天狐显真-激化", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "野干役咒·杀生樱":
                        self.skill_E(dmg)
                    case "野干役咒·杀生樱-激化":
                        self.skill_E(dmg, "超激化")
                    case "大密法·天狐显真":
                        self.skill_Q(dmg)
                    case "大密法·天狐显真-激化":
                        self.skill_Q(dmg, "超激化")
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "激化狐":
                return {
                    "充能效率阈值": 140,
                    "野干役咒·杀生樱": 0,
                    "野干役咒·杀生樱-激化": 10,
                    "大密法·天狐显真": 0,
                    "大密法·天狐显真-激化": 10,
                }
            case "纯雷狐":
                return {
                    "充能效率阈值": 140,
                    "野干役咒·杀生樱": 10,
                    "野干役咒·杀生樱-激化": 0,
                    "大密法·天狐显真": 10,
                    "大密法·天狐显真-激化": 0,
                }
            case _:
                return {
                    "充能效率阈值": 140,
                    "野干役咒·杀生樱": -1,
                    "野干役咒·杀生樱-激化": 10,
                    "大密法·天狐显真": -1,
                    "大密法·天狐显真-激化": 10,
                }

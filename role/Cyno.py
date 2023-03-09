from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, DmgBonus, Multiplier
from ._model import Role


class Cyno(Role):
    name = "赛诺"

    def buff_T1(self, buff_info: BuffInfo):
        """落羽的裁择"""
        buff_info.buff = Buff(
            dsc="末途真眼状态下，秘仪·律渊渡魂增伤+35%",
            target="E",
            dmg_bonus=0.35,
        )

    T2_NA_scaler: int = 0
    """启途誓使状态下普攻额外倍率"""
    T2_bolt_scaler: int = 0
    """渡荒之雷额外倍率"""

    def buff_T2(self, buff_info: BuffInfo):
        """九弓的执命"""
        self.T2_NA_scaler = 150
        self.T2_bolt_scaler = 250
        buff_info.buff = Buff(
            dsc="启途誓使状态下普攻倍率+150%精通，渡荒之雷倍率+250%精通",
        )

    def buff_C2(self, buff_info: BuffInfo):
        """令仪·引谒归灵"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4", "5"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"普攻命中叠层，总雷伤+{s*10}%，持续4秒",
            elem_dmg_bonus=DmgBonus(electro=0.1 * s),
        )

    def skill_E(self, dmg_info: Dmg):
        """秘仪·律渊渡魂"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("秘仪·律渊渡魂", self.talents[1].level, "冥祭伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="electro",
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
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="落羽的裁择",
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="九弓的执命",
                    )
                )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="令仪·引谒归灵",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="普攻命中叠层，①~⑤每层：雷伤+10%",
                        label=labels.get("令仪·引谒归灵", "5"),
                    ),
                )
            )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="圣仪·煟煌随狼行·启途誓使",
                buff_type="propbuff",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "落羽的裁择":
                    self.buff_T1(buff)
                case "九弓的执命":
                    self.buff_T2(buff)
                case "令仪·引谒归灵":
                    self.buff_C2(buff)
                case "圣仪·煟煌随狼行·启途誓使":
                    self.buff_Q(buff)

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
                name="秘仪·律渊渡魂",
                dsc="E冥祭伤害",
                weight=weights.get("秘仪·律渊渡魂", 0),
                exclude_buff=ex_buffs.get("秘仪·律渊渡魂", []),
            ),
            
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "秘仪·律渊渡魂":
                        self.skill_E(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "秘仪·律渊渡魂": 10,
                }

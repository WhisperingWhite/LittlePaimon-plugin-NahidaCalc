from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, Multiplier, PoFValue
from ._model import Role


class Xiao(Role):
    name = "魈"

    def buff_T1(self, buff_info: BuffInfo):
        """降魔·平妖大圣"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4", "5"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"靖妖傩舞状态下随时间叠层，增伤+{5*s}%",
            dmg_bonus=0.05 * s,
        )

    def buff_T2(self, buff_info: BuffInfo):
        """坏劫·国土碾尘"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3"]:
                setting.state, s = f"{x}层", int(x)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"施放风轮两立叠层7秒内，风轮两立增伤+{15*s}",
            dmg_bonus=0.15 * s,
        )

    def buff_C2(self, buff_info: BuffInfo):
        """空劫·虚空华开敷变"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="处于后台时，充能+25%",
            recharge=0.25,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """神通·诸苦灭尽"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="生命值低于50％，防御+100%",
            defense=PoFValue(percent=1),
        )

    def skill_A(self, dmg_info: Dmg):
        """卷积微尘"""
        calc = self.create_calc()
        _, scaler = [
            float(num)
            for num in self.get_scaler(
                "普通攻击·卷积微尘", self.talents[0].level, "低空/高空坠地冲击伤害"
            )
            .replace("%", "")
            .split("/")
        ]
        calc.set(
            value_type="PA",
            elem_type="anemo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def skill_E(self, dmg_info: Dmg):
        """风轮两立"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("风轮两立", self.talents[1].level, "技能伤害").replace("%", "")
        )
        calc.set(
            value_type="E",
            elem_type="anemo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_Q(self, buff_info: BuffInfo):
        """靖妖傩舞"""
        dmg_bonus = float(
            self.get_scaler("靖妖傩舞", self.talents[2].level, "普通攻击/重击/下落攻击伤害提升").replace(
                "%", ""
            )
        )
        buff_info.buff = Buff(
            dsc=f"夜叉傩面状态下，普攻、重击、下落增伤+{dmg_bonus}%",
            target=["NA", "CA", "PA"],
            dmg_bonus=dmg_bonus,
        )

    category: str = "站场主C"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["站场主C"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "站场主C":
                return ["攻击", "攻击%", "风伤", "暴击", "暴伤"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="降魔·平妖大圣",
                    setting=BuffSetting(
                        dsc="靖妖傩舞状态下，每3秒叠层，基础1层，①~⑤每层增伤+5%",
                        label=labels.get("降魔·平妖大圣", "5"),
                    ),
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="坏劫·国土碾尘",
                        setting=BuffSetting(
                            dsc="施放风轮两立叠层，⓪~③每层风轮两立增伤+15%",
                            label=labels.get("坏劫·国土碾尘", "3"),
                        ),
                    )
                )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="空劫·虚空华开敷变",
                    buff_type="propbuff",
                    setting=BuffSetting(label=labels.get("空劫·虚空华开敷变", "○")),
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="神通·诸苦灭尽",
                        buff_type="propbuff",
                        setting=BuffSetting(label=labels.get("神通·诸苦灭尽", "○")),
                    )
                )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="靖妖傩舞",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "降魔·平妖大圣":
                    self.buff_T1(buff)
                case "坏劫·国土碾尘":
                    self.buff_T2(buff)
                case "空劫·虚空华开敷变":
                    self.buff_C2(buff)
                case "神通·诸苦灭尽":
                    self.buff_C4(buff)
                case "靖妖傩舞":
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
                source="A",
                name="卷积微尘",
                dsc="A高空下落",
                weight=weights.get("卷积微尘", 0),
                exclude_buff=ex_buffs.get("卷积微尘", []),
            ),
            Dmg(
                index=2,
                source="E",
                name="风轮两立",
                dsc="E一段",
                weight=weights.get("风轮两立", 0),
                exclude_buff=ex_buffs.get("卷积微尘", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "卷积微尘":
                        self.skill_A(dmg)
                    case "风轮两立":
                        self.skill_E(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "站场主C":
                return {
                    "充能效率阈值": 120,
                    "卷积微尘": 10,
                    "风轮两立": 10,
                }
            case _:
                return {
                    "充能效率阈值": 100,
                    "卷积微尘": 10,
                    "风轮两立": 10,
                }

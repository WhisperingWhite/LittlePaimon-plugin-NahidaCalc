from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class Rosaria(Role):
    name = "罗莎莉亚"

    def buff_T1(self, buff_info: BuffInfo):
        """聆听忏悔的幽影"""
        buff_info.buff = Buff(
            dsc="噬罪的告解从背后攻击，暴击+12%，持续5秒",
            crit_rate=0.12,
        )

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """暗中支援的黯色"""
        crit_rate = min(prop.crit_rate * 0.15, 0.15)
        buff_info.buff = Buff(
            dsc=f"施放终命的圣礼10秒内，基于自身暴击，提升队友暴击(+{crit_rate:.1f}%)",
            crit_rate=crit_rate,
        )

    def buff_C1(self, buff_info: BuffInfo):
        """罪之导引"""
        buff_info.buff = Buff(
            dsc="攻击造成暴击4秒内，普攻增伤+10%",
            target="NA",
            dmg_bonus=0.1,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """代行裁判"""
        buff_info.buff = Buff(
            dsc="终命的圣礼命中10秒内，敌人物抗-20%",
            resist_reduction=DmgBonus(phy=0.2),
        )

    def skill_Q(self, dmg_info: Dmg):
        """终命的圣礼"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("终命的圣礼", self.talents[2].level, "冰枪持续伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="cryo",
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
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="聆听忏悔的幽影",
                    buff_type="propbuff",
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="暗中支援的黯色",
                        buff_range="all",
                        buff_type="transbuff",
                    )
                )
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="罪之导引",
                )
            )
            if self.info.constellation >= 6:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C6",
                        name="代行裁判",
                        buff_range="all",
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "聆听忏悔的幽影":
                    self.buff_T1(buff)
                case "暗中支援的黯色":
                    self.buff_T2(buff, prop)
                case "罪之导引":
                    self.buff_C1(buff)
                case "代行裁判":
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
                name="终命的圣礼",
                dsc="Q冰枪持续每段",
                weight=weights.get("终命的圣礼", 0),
                exclude_buff=ex_buffs.get("终命的圣礼", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "终命的圣礼":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 180,
                    "终命的圣礼": 10,
                }

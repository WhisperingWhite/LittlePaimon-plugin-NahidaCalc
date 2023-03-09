from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, Multiplier, ReaFactor
from ..dmg_calc import DmgCalc
from ._model import Role


class Nilou(Role):
    name = "妮露"

    def buff_T1(self, buff_info: BuffInfo):
        """折旋落英之庭"""
        buff_info.buff = Buff(
            dsc="处于金杯的丰馈下，受到草元素攻击时，全队精通+100",
            elem_mastery=100,
        )

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """翩舞永世之梦"""
        reac_coeff = min((prop.hp - 30000) / 1000 * 0.09, 4)
        buff_info.buff = Buff(
            dsc=f"妮露生命值上限超过30000的部分，每1000点丰穰之核反应系数+9%，至多400%(+{reac_coeff*100}%)",
            reaction_coeff=ReaFactor(bloom=reac_coeff),
        )

    C1_lumi: float = 0.0
    """C1水月增伤"""

    def buff_C1(self, buff_info: BuffInfo):
        """却月的轻舞"""
        buff_info.buff = Buff(
            dsc="水月增伤+65%",
        )
        self.C1_lumi = 0.65

    def buff_C2(self, buff_info: BuffInfo):
        """星天的花雨"""
        buff_info.buff = Buff(
            dsc="金杯的丰馈下，造成水伤10秒内，水抗-35%，触发绽放10秒内，草抗-35%",
            resist_reduction=DmgBonus(hydro=0.35, dendro=0.35),
        )

    def buff_C4(self, buff_info: BuffInfo):
        """挽漪的节音"""
        buff_info.buff = Buff(
            dsc="七域舞步的第三段命中8秒内，浮莲舞步·远梦聆泉增伤+50%",
            target="Q",
            crit_rate=0.5,
        )

    def buff_C6(self, buff_info: BuffInfo, prop: DmgCalc):
        """断霜的弦歌"""
        s = (min(prop.hp, 50000) - min(self.prop.hp, 50000)) / 1000
        buff_info.buff = Buff(
            dsc="每1000点生命值上限，暴击+0.6%，暴伤+1.2%",
            crit_rate=0.006 * s,
            crit_dmg=0.012 * s,
        )

    def bloom(self, dmg_info: Dmg):
        """金杯的丰馈"""
        calc = self.create_calc()
        calc.set(
            reaction_type="绽放",
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_trans_reac_dmg())

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
                    name="折旋落英之庭",
                    buff_range="all",
                    buff_type="propbuff",
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="翩舞永世之梦",
                    )
                )
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="却月的轻舞",
                )
            )
            if self.info.constellation >= 2:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C2",
                        name="星天的花雨",
                    )
                )
                if self.info.constellation >= 4:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C4",
                            name="挽漪的节音",
                        )
                    )
                    if self.info.constellation >= 6:
                        output.append(
                            BuffInfo(
                                source=f"{self.name}-C6",
                                name="断霜的弦歌",
                                buff_range="transbuff",
                            )
                        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "折旋落英之庭":
                    self.buff_T1(buff)
                case "翩舞永世之梦":
                    self.buff_T2(buff, prop)
                case "却月的轻舞":
                    self.buff_C1(buff)
                case "星天的花雨":
                    self.buff_C2(buff)
                case "挽漪的节音":
                    self.buff_C4(buff)
                case "断霜的弦歌":
                    self.buff_C6(buff, prop)

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
                name="金杯的丰馈",
                dsc="每枚种子爆炸",
                weight=weights.get("金杯的丰馈", 0),
                exclude_buff=ex_buffs.get("金杯的丰馈", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "金杯的丰馈":
                        self.bloom(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "金杯的丰馈": 10,
                }

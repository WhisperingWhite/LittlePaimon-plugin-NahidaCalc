from ..classmodel import Dmg, Buff, BuffInfo, BuffSetting, PoFValue, Multiplier
from ._model import Role
from ..dmg_calc import DmgCalc


class Candace(Role):
    name = "坎蒂丝"

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """漫沙陨穹"""
        dmg_bonus = prop.hp / 1000 * 0.005
        buff_info.buff = Buff(
            dsc=f"赤冕祝祷状态下，每1000点生命上限，普攻增伤+0.5%(+{dmg_bonus*100}%)",
            target="NA",
            dmg_bonus=dmg_bonus,
        )

    def buff_C2(self, buff_info: BuffInfo):
        """贯月的耀锋"""
        buff_info.buff = Buff(
            dsc=f"圣仪·苍鹭庇卫命中15秒内，生命上限+20%(+{self.prop.hp_base*0.2})",
            hp=PoFValue(percent=0.2),
        )

    def buff_Q(self, buff_info: BuffInfo):
        """圣仪·灰鸰衒潮·赤冕祝祷"""
        buff_info.buff = Buff(
            dsc="赤冕祝祷状态下，普攻增伤+20%",
            target="NA",
            dmg_bonus=0.2,
        )

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T2",
                    name="漫沙陨穹",
                    buff_range="all",
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="贯月的耀锋",
                    buff_type="propbuff",
                )
            )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="圣仪·灰鸰衒潮·赤冕祝祷",
                buff_range="all",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "漫沙陨穹":
                    self.buff_T2(buff, prop)
                case "贯月的耀锋":
                    self.buff_C2(buff)
                case "圣仪·灰鸰衒潮·赤冕祝祷":
                    self.buff_Q(buff)

    def weight(self, weights: dict, ex_buffs: dict):
        """伤害权重"""
        self.dmg_list = [
            Dmg(
                index=0,
                name="充能效率阈值",
                weight=weights.get("充能效率阈值", 100),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 160,
                }

from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class PlayerElectric(Role):
    name = "雷主"

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """回响的轰雷"""
        recharge = prop.recharge * 0.1
        buff_info.buff = Buff(
            dsc=f"基于充能，雷影剑的丰穰勾玉额外充能+{recharge:.1f}%",
            recharge=recharge,
        )

    def buff_C2(self, buff_info: BuffInfo):
        """震怒的苍雷"""
        buff_info.buff = Buff(
            dsc="雷轰电转的威光命中8秒内，雷抗-15%",
            resist_reduction=DmgBonus(electro=0.15),
        )

    def buff_E(self, buff_info: BuffInfo):
        """雷影剑·丰穰勾玉"""
        buff_info.buff = Buff(
            dsc="吸收丰穰勾玉，充能+20%",
            recharge=0.2,
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
                    name="回响的轰雷",
                    buff_range="active",
                    buff_type="propbuff",
                )
            )
        # 命座
        if self.info.ascension >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="震怒的苍雷",
                    buff_range="all",
                )
            )
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="雷影剑·丰穰勾玉",
                buff_range="active",
                buff_type="propbuff",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "回响的轰雷":
                    self.buff_T2(buff, prop)
                case "震怒的苍雷":
                    self.buff_C2(buff)
                case "雷影剑·丰穰勾玉":
                    self.buff_E(buff)

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
                    "充能效率阈值": 250,
                }

from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, Multiplier
from ..dmg_calc import DmgCalc
from ._model import Role


class Kazuha(Role):
    name = "万叶"

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """风物之诗咏"""
        dmg_bonus = prop.elem_mastery * 0.04 / 100
        buff_info.buff = Buff(
            dsc="触发扩散反应8秒内，",
        )
        setting = buff_info.setting
        for label in setting.label:
            match label:
                case x if x in ["火", "水", "雷", "冰"]:
                    setting.state += x
                    buff_info.buff.dsc += f"{x}伤+{dmg_bonus}%"
                    buff_info.buff.elem_dmg_bonus.set({x: dmg_bonus})
        setting.state += "扩散"

    def buff_C2(self, buff_info: BuffInfo):
        """山岚残芯"""
        buff_info.buff = Buff(
            dsc="流风秋野持续期间，万叶精通+200，场上的其他角色精通+200",
            elem_mastery=200,
        )

    def buff_C6(self, buff_info: BuffInfo, prop: DmgCalc):
        """血赤叶红"""
        dmg_bonus = prop.elem_mastery * 0.2 / 100
        buff_info.buff = Buff(
            dsc=f"每点元素精通，提升普攻、重击和下落增伤+0.2%(+{dmg_bonus*100}%)",
            target=["NA", "CA", "PA"],
            dmg_bonus=dmg_bonus,
        )

    def swirls(self, dmg_info: Dmg):
        """扩散伤害"""
        calc = self.create_calc()
        calc.set(
            reaction_type="扩散",
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
        if self.info.ascension >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T2",
                    name="风物之诗咏",
                    buff_type="transbuff",
                    setting=BuffSetting(
                        dsc="触发扩散（火，水，雷，冰）：对应元素增伤基于元素精通，可共存",
                        label=labels.get("风物之诗咏", "火"),
                    ),
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="山岚残芯",
                    buff_range="active",
                    buff_type="propbuff",
                )
            )
            if self.info.constellation >= 6:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C6",
                        name="血赤叶红",
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "风物之诗咏":
                    self.buff_T2(buff)
                case "山岚残芯":
                    self.buff_C2(buff)
                case "血赤叶红":
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
                name="扩散",
                dsc="扩散伤害",
                weight=weights.get("扩散", 0),
                exclude_buff=ex_buffs.get("扩散", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "扩散":
                        self.swirls(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 160,
                    "扩散": 10,
                }

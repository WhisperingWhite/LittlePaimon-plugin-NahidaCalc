from ..classmodel import (
    Buff,
    BuffInfo,
    BuffSetting,
    Dmg,
    DmgBonus,
    Multiplier,
    PoFValue,
)
from ._model import Role


class Gorou(Role):
    name = "五郎"

    def buff_T1(self, buff_info: BuffInfo):
        """不畏风雨"""
        buff_info.buff = Buff(
            dsc="施放兽牙逐突形胜战法12秒内，全队防御+25%",
            defense=PoFValue(percent=0.25),
        )

    T2_E_scaler: float = 0.0
    """T2对E基础伤害加成"""
    T2_Q_scaler: float = 0.0
    """T2对Q基础伤害加成"""

    def buff_T2(self, buff_info: BuffInfo):
        """报恩之守"""
        self.T2_E_scaler = 156
        self.T2_Q_scaler = 15.6
        buff_info.buff = Buff(
            dsc="元素战技倍率+156%防御，元素爆发基础伤害+15.6%防御",
        )

    def buff_C6(self, buff_info: BuffInfo):
        """犬勇•忠如山"""
        setting = buff_info.setting
        match setting.label:
            case "1":
                setting.state, geo_crit_dmg = "「坚牢」", 0.1
            case "2":
                setting.state, geo_crit_dmg = "「难破」", 0.2
            case x if x in ["3", "4"]:
                setting.state, geo_crit_dmg = "「摧碎」", 0.4
            case _:
                setting.state = "×"
        buff_info.buff = Buff(
            dsc=f"施放大将旗指物12秒内，岩伤暴伤+{geo_crit_dmg*100}%",
            crit_dmg=geo_crit_dmg,
        )

    def buff_E(self, buff_info: BuffInfo):
        """犬坂吠吠方圆阵"""
        setting = buff_info.setting
        match setting.label:
            case "1":
                setting.state, geo_bonus = "「坚牢」", 0
            case "2":
                setting.state, geo_bonus = "「难破」", 0
            case x if x in ["3", "4"]:
                setting.state, geo_bonus = "「摧碎」", 0.1
            case _:
                setting.state = "×"
        fix_value = float(self.get_scaler("犬坂吠吠方圆阵", self.talents[1].level, "防御力提升"))
        buff_info.buff = Buff(
            dsc=f"全队提高防御+{fix_value}，岩伤+{geo_bonus*100}%",
            defense=PoFValue(fix=fix_value),
            elem_dmg_bonus=DmgBonus(geo=geo_bonus),
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
                    name="不畏风雨",
                    buff_type="propbuff",
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="报恩之守",
                    )
                )
            # 命座
            if self.info.constellation >= 6:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C6",
                        name="犬勇•忠如山",
                        buff_range="all",
                        setting=BuffSetting(
                            dsc="依据施放时的领域等级，①~③岩伤暴伤+10/20/40%",
                            label=labels.get("犬勇•忠如山", "3"),
                        ),
                    )
                )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="犬坂吠吠方圆阵",
                buff_range="all",
                buff_type="propbuff",
                setting=BuffSetting(
                    dsc="依据队伍中岩元素角色数量，①~③获得加成",
                    label=labels.get("犬勇•忠如山", "3"),
                ),
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "不畏风雨":
                    self.buff_T1(buff)
                case "报恩之守":
                    self.buff_T2(buff)
                case "犬勇•忠如山":
                    self.buff_C6(buff)
                case "犬坂吠吠方圆阵":
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
                    "充能效率阈值": 200,
                }

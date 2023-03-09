from ..classmodel import (
    Buff,
    BuffInfo,
    BuffSetting,
    Dmg,
    Multiplier,
    PoFValue,
    FixValue,
)
from ..dmg_calc import DmgCalc
from ._model import Role


class Yunjin(Role):
    name = "云堇"

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """莫从恒蹊"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3"]:
                setting.state, scaler = f"{x}种", int(x) * 0.025
            case "4":
                setting.state, scaler = f"{x}种", 0.115
            case _:
                setting.state, scaler = "×", 0
        extra_dmg = scaler * prop.defense
        buff_info.buff = Buff(
            dsc=f"队伍中存在{x}种元素的角色，基于防御，全队普攻基础伤害+{extra_dmg:.0f}",
            fix_value=FixValue(dmg=extra_dmg),
        )

    def buff_C2(self, buff_info: BuffInfo):
        """诸般切末"""
        buff_info.buff = Buff(
            dsc="施放破嶂见旌仪12s内，全队普攻增伤+15%",
            target="NA",
            dmg_bonus=0.15,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """昇堂吊云"""
        buff_info.buff = Buff(
            dsc=f"触发结晶12s内，防御+20%(+{self.prop.def_base*0.2:.0f})",
            defense=PoFValue(percent=0.2),
        )

    def buff_Q(self, buff_info: BuffInfo, prop: DmgCalc):
        """破嶂见旌仪"""
        scaler = float(
            self.get_scaler("破嶂见旌仪", self.talents[2].level, "防御力提升").replace(
                "伤害值提升", ""
            )
        )
        extra_dmg = scaler * prop.defense / 100
        buff_info.buff = Buff(
            dsc=f"飞云旗阵状态下，全队普攻基础伤害+{extra_dmg:.0f}",
            fix_value=FixValue(dmg=extra_dmg),
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
                    name="莫从恒蹊",
                    buff_range="all",
                    setting=BuffSetting(
                        dsc="队伍中存在①~④种不同元素类型的角色，提升普攻基础伤害",
                        label=labels.get("莫从恒蹊", "3"),
                    ),
                )
            )
            # 命座
            if self.info.constellation >= 2:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C2",
                        name="诸般切末",
                        buff_range="all",
                    )
                )
                if self.info.constellation >= 4:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C4",
                            name="昇堂吊云",
                            buff_type="propbuff",
                        )
                    )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="破嶂见旌仪",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "莫从恒蹊":
                    self.buff_T2(buff, prop)
                case "诸般切末":
                    self.buff_C2(buff)
                case "昇堂吊云":
                    self.buff_C4(buff)
                case "破嶂见旌仪":
                    self.buff_Q(buff, prop)

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

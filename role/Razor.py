from ..classmodel import Dmg, Buff, BuffInfo, Multiplier
from ._model import Role


class Razor(Role):
    name = "雷泽"

    def buff_T2(self, buff_info: BuffInfo):
        """饥饿"""
        buff_info.buff = Buff(
            dsc="元素能量低于50%，充能+30%",
            recharge=0.3,
        )

    def buff_C1(self, buff_info: BuffInfo):
        """狼性"""
        buff_info.buff = Buff(
            dsc="获取元素球8秒内，增伤+10%",
            dmg_bonus=0.1,
        )

    def buff_C2(self, buff_info: BuffInfo):
        """压制"""
        buff_info.buff = Buff(
            dsc="敌方生命低于30%，暴击+10%",
            crit_rate=0.1,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """撕咬"""
        buff_info.buff = Buff(
            dsc="利爪与苍雷点按命中7秒内，减防+15%",
            def_reduction=0.15,
        )

    def skill_A(self, dmg_info: Dmg):
        """钢脊"""
        calc = self.create_calc()
        scaler = sum(
            [
                float(i.replace("%", ""))
                for i in self.get_scaler(
                    "普通攻击·钢脊",
                    self.talents[0].level,
                    "一段伤害",
                    "二段伤害",
                    "三段伤害",
                    "四段伤害",
                )
            ]
        )
        calc.set(
            value_type="NA",
            elem_type="phy",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []

        output.append(self.setting_conduct(labels))
        # 天赋
        if self.info.ascension >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T2",
                    name="饥饿",
                    buff_type="propbuff",
                )
            )
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="狼性",
                )
            )
            if self.info.constellation >= 2:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C2",
                        name="压制",
                    )
                )
                if self.info.constellation >= 4:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C4",
                            name="撕咬",
                            buff_range="all",
                        )
                    )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "超导":
                    self.buff_conduct(buff)
                case "饥饿":
                    self.buff_T2(buff)
                case "狼性":
                    self.buff_C1(buff)
                case "压制":
                    self.buff_C2(buff)
                case "撕咬":
                    self.buff_C4(buff)

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
                name="钢脊",
                dsc="A一轮四段",
                weight=weights.get("钢脊", 0),
                exclude_buff=ex_buffs.get("钢脊", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "钢脊":
                        self.skill_A(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "钢脊": 10,
                }

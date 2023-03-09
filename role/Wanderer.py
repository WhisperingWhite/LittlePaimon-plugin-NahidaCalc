from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg, Multiplier
from ._model import Role


class Wanderer(Role):
    name = "流浪者"

    def buff_T1(self, buff_info: BuffInfo):
        """拾玉得花"""
        buff_info.buff = Buff(
            dsc="施放羽画·风姿华歌时",
        )
        max_buff = 3 if self.info.constellation >= 4 else 2
        setting = buff_info.setting
        for label in setting.label[:max_buff]:
            match label:
                case "火":
                    setting.state += "火"
                    buff_info.buff.dsc += f"，接触火元素，攻击+30%({self.prop.atk_base*0.3})%"
                    buff_info.buff.atk.percent = 0.3
                case "水":
                    setting.state += "水"
                case "雷":
                    setting.state += "雷"
                case "冰":
                    setting.state += "冰"
                    buff_info.buff.dsc += "，接触冰元素，暴击+20%"
                    buff_info.buff.crit_rate = 0.2
        setting.state += "强化"

    def buff_C2(self, buff_info: BuffInfo):
        """二番·箙岛月白浪"""
        buff_info.buff = Buff(
            dsc="优风倾姿状态下，依据消耗的空居力，狂言·式乐五番最大增伤+200%",
            target="Q",
            dmg_bonus=2,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """四番·花月歌浮舟"""
        buff_info.buff = Buff(
            dsc="拾玉得花元素效果上限提升为3种",
        )

    def skill_Q(self, dmg_info: Dmg):
        """狂言·式乐五番"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("狂言·式乐五番", self.talents[2].level, "技能伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="anemo",
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
                    name="拾玉得花",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="触发狂言·式乐五番（火，水，雷，冰）：对应元素增伤基于元素精通，可共存",
                        label=labels.get("拾玉得花", "火"),
                    ),
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="二番·箙岛月白浪",
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="四番·花月歌浮舟",
                    )
                )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "拾玉得花":
                    self.buff_T1(buff)
                case "二番·箙岛月白浪":
                    self.buff_C2(buff)
                case "四番·花月歌浮舟":
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
                source="Q",
                name="狂言·式乐五番",
                dsc="Q总爆发",
                weight=weights.get("狂言·式乐五番", 0),
                exclude_buff=ex_buffs.get("狂言·式乐五番", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "狂言·式乐五番":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "狂言·式乐五番": 10,
                }

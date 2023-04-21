from ..classmodel import Dmg, Buff, BuffInfo, BuffSetting, PoFValue, Multiplier
from ._model import Role


class Ayato(Role):
    name = "绫人"

    def buff_C1(self, buff_info: BuffInfo):
        """镜华风姿"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc="对于生命值低于50%的敌人，瞬水剑增伤+40%",
            target="NA",
            dmg_bonus=0.4,
        )

    def buff_C2(self, buff_info: BuffInfo):
        """世有源泉"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        buff_info.buff = Buff(
            dsc=f"浪闪上限提升至5层，至少3层浪闪状态下，生命上限+50%(+{self.prop.hp_base*0.5:.0f})",
            hp=PoFValue(percent=0.5),
        )
        self.max_stack += 1

    def skill_E(self, dmg_info: Dmg):
        """神里流·镜花·泷廻鉴花"""
        calc = self.create_calc()
        scaler = sum(
            [
                float(i.replace("%", ""))
                for i in self.get_scaler(
                    "神里流·水囿",
                    self.talents[1].level,
                    "一段瞬水剑伤害",
                    "二段瞬水剑伤害",
                    "三段瞬水剑伤害",
                )
            ]
        )
        calc.set(
            value_type="NA",
            elem_type="hydro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_E(self, buff_info: BuffInfo):
        """神里流·镜花·浪闪"""
        multip = float(
            self.get_scaler("神里流·镜花", self.talents[1].level, "浪闪伤害值提高").replace(
                "%最大生命值/层", ""
            )
        )
        setting = buff_info.setting
        match setting.label:
            case x if x in ["1", "2", "3", "4", "5"]:
                setting.state, s = f"{x}层", min(int(x), self.max_stack)
            case _:
                setting.state, s = "×", 0
        buff_info.buff = Buff(
            dsc=f"瞬水剑倍率+{multip*s}%最大生命值",
            target="NA",
            multiplier=Multiplier(hp=multip * s),
        )

    def skill_Q(self, dmg_info: Dmg):
        """神里流·水囿·水花剑"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("神里流·水囿", self.talents[2].level, "水花剑伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="hydro",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    max_stack = 4
    """浪闪最大层数"""

    def buff_Q(self, buff_info: BuffInfo):
        """神里流·水囿"""
        if buff_info.setting.label == "-":
            buff_info.setting.state = "×"
        dmg_bonus = float(
            self.get_scaler("神里流·水囿", self.talents[2].level, "普通攻击伤害提升").replace(
                "%", ""
            )
        )
        buff_info.buff = Buff(
            dsc=f"神里流·水囿领域内，普攻增伤+{dmg_bonus}%",
            target="NA",
            dmg_bonus=dmg_bonus / 100,
        )

    category: str = "站场水C"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["站场水C"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "站场水C":
                return ["攻击", "攻击%", "水伤", "暴击", "暴伤", "生命%"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="镜华风姿",
                    setting=BuffSetting(label=labels.get("镜华风姿", "○")),
                )
            )
            if self.info.constellation >= 2:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C2",
                        name="世有源泉",
                        buff_type="propbuff",
                        setting=BuffSetting(label=labels.get("世有源泉", "○")),
                    )
                )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="神里流·镜花·浪闪",
                setting=BuffSetting(
                    dsc="瞬水剑攻击命中，赋予「浪闪」效果，每层提升瞬水剑倍率",
                    label=labels.get("神里流·镜花·浪闪", "5"),
                ),
            )
        )
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="神里流·水囿",
                buff_range="all",
                label=labels.get("神里流·水囿", "5"),
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "镜华风姿":
                    self.buff_C1(buff)
                case "世有源泉":
                    self.buff_C2(buff)
                case "神里流·镜花·浪闪":
                    self.buff_E(buff)
                case "神里流·水囿":
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
                source="E",
                name="神里流·镜花·泷廻鉴花",
                dsc="E瞬水剑一轮三段",
                weight=weights.get("神里流·水囿·泷廻鉴花", 0),
                exclude_buff=ex_buffs.get("神里流·水囿·泷廻鉴花", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="神里流·水囿·水花剑",
                dsc="Q水花剑每段",
                weight=weights.get("神里流·水囿·水花剑", 0),
                exclude_buff=ex_buffs.get("神里流·水囿·水花剑", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "神里流·镜花·泷廻鉴花":
                        self.skill_E(dmg)
                    case "神里流·水囿·水花剑":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "站场水C":
                return {
                    "充能效率阈值": 100,
                    "神里流·镜花·泷廻鉴花": 10,
                    "神里流·水囿·水花剑": -1,
                }
            case _:
                return {
                    "充能效率阈值": 100,
                    "神里流·镜花·泷廻鉴花": 10,
                    "神里流·水囿·水花剑": -1,
                }

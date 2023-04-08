from ..classmodel import (
    Buff,
    BuffInfo,
    BuffSetting,
    Dmg,
    DmgBonus,
    Multiplier,
    PoFValue,
)
from ..dmg_calc import DmgCalc
from ._model import Role


class Shougun(Role):
    name = "影"

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """殊胜之御体"""
        electro_dmg_bonus = (prop.recharge - self.prop.recharge) * 0.4 / 100
        buff_info.buff = Buff(
            dsc=f"基于充能超过100%的部分，雷伤+{electro_dmg_bonus*100:.1f}%",
            elem_dmg_bonus=DmgBonus(electro=electro_dmg_bonus),
        )

    def buff_C2(self, buff_info: BuffInfo):
        """斩铁断金"""
        buff_info.buff = Buff(
            dsc="梦想一心状态期间，无视防御+60%",
            target="Q",
            def_piercing=0.6,
        )

    def buff_C4(self, buff_info: BuffInfo, prop: DmgCalc):
        """誓奉常道"""
        buff_info.buff = Buff(
            dsc=f"梦想一心状态结束10秒内，队友攻击+30%(+{prop.atk_base*0.3:.0f})",
            atk=PoFValue(percent=0.3),
        )

    def buff_E(self, buff_info: BuffInfo):
        """神变·恶曜开眼"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["40", "50", "60", "70", "80", "90"]:
                setting.state, energy = f"{x}点能量", int(x)
            case _:
                setting.state, energy = "×", 0
        scaler = float(
            self.get_scaler("神变·恶曜开眼", self.talents[1].level, "元素爆发伤害提高")
            .replace("%", "")
            .replace("每点元素能量", "")
        )
        dmg_bonus = energy * scaler / 100
        buff_info.buff = Buff(
            dsc=f"雷罚恶曜之眼持续期间，基于元素能量，元素爆发增伤+{dmg_bonus*100}%",
            target="Q",
            dmg_bonus=dmg_bonus,
        )

    hitotachi_bonus: float = 0.0
    """梦想一刀加成倍率"""
    isshin_bonus: float = 0.0
    """梦想一心加成倍率"""

    def buff_Q(self, buff_info: BuffInfo):
        """奥义·梦想真说·诸愿百眼之轮"""
        setting = buff_info.setting
        if x := setting.label.isdigit():
            setting.state, energy = f"{x}层", min(int(x), 60)
        else:
            setting.state, energy = "×", 0
        scaler1, scaler2 = [
            float(num)
            for num in self.get_scaler("奥义·梦想真说", self.talents[2].level, "愿力加成")
            .replace("%", "")
            .replace("每层", "")
            .replace("攻击力", "")
            .split("/")
        ]
        self.hitotachi_bonus = energy * scaler1
        self.isshin_bonus = energy * scaler2
        buff_info.buff = Buff(
            dsc=f"梦想一刀倍率+{self.hitotachi_bonus}%，梦想一心倍率+{self.isshin_bonus}%",
        )

    def skill_Q(self, dmg_info: Dmg):
        """奥义•梦想真说"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("奥义·梦想真说", self.talents[2].level, "梦想一刀基础伤害").replace(
                "%", ""
            )
        )
        calc.set(
            value_type="Q",
            elem_type="electro",
            multiplier=Multiplier(atk=scaler + self.hitotachi_bonus),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def hyperbloom(self, dmg_info: Dmg):
        """超绽放"""
        calc = self.create_calc()
        calc.set(
            reaction_type="超绽放",
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_trans_reac_dmg())

    category: str = "充能前台"
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list = ["充能前台", "精通后台"]
    """可选流派"""

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        match self.category:
            case "充能前台":
                return ["攻击", "攻击%", "雷伤", "暴击", "暴伤", "充能"]
            case "精通后台":
                return ["精通"]
            case _:
                return ["攻击", "攻击%", "雷伤", "暴击", "暴伤", "充能"]

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        if self.info.ascension >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T2",
                    name="殊胜之御体",
                    buff_type="transbuff",
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="斩铁断金",
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="誓奉常道",
                        buff_range="party",
                        buff_type="propbuff",
                    )
                )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-E",
                name="神变•恶曜开眼",
                buff_range="all",
                setting=BuffSetting(
                    dsc="雷罚恶曜之眼持续期间，基于元素能量，全队元素爆发增伤",
                    label=labels.get("神变•恶曜开眼", "90"),
                ),
            )
        )
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="奥义•梦想真说·诸愿百眼之轮",
                setting=BuffSetting(
                    dsc="基于诸愿百眼之轮愿力，最大60层，加成梦想一刀和梦想一心倍率",
                    label=labels.get("奥义•梦想真说·诸愿百眼之轮", "60"),
                ),
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "殊胜之御体":
                    self.buff_T2(buff, prop)
                case "斩铁断金":
                    self.buff_C2(buff)
                case "誓奉常道":
                    self.buff_C4(buff, prop)
                case "神变•恶曜开眼":
                    self.buff_E(buff)
                case "奥义•梦想真说·诸愿百眼之轮":
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
                source="Q",
                name="奥义•梦想真说",
                dsc="Q梦想一刀",
                weight=weights.get("奥义•梦想真说", 0),
                exclude_buff=ex_buffs.get("奥义•梦想真说", []),
            ),
            Dmg(
                index=2,
                name="超绽放",
                dsc="每枚种子",
                weight=weights.get("超绽放", 0),
                exclude_buff=ex_buffs.get("超绽放", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "奥义•梦想真说":
                        self.skill_Q(dmg)
                    case "超绽放":
                        self.hyperbloom(dmg)
        return self.dmg_list

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case "充能前台":
                return {
                    "充能效率阈值": 270,
                    "奥义•梦想真说": 10,
                    "超绽放": 0,
                }
            case "精通后台":
                return {
                    "充能效率阈值": 150,
                    "奥义•梦想真说": 0,
                    "超绽放": 10,
                }
            case _:
                return {
                    "充能效率阈值": 250,
                    "奥义•梦想真说": 10,
                    "超绽放": -1,
                }

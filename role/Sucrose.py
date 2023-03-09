from ..classmodel import Buff, BuffInfo, BuffSetting, Dmg
from ..dmg_calc import DmgCalc
from ._model import Role


class Sucrose(Role):
    name = "砂糖"

    def buff_T1(self, buff_info: BuffInfo):
        """触媒置换术"""
        buff_info.buff = Buff(
            dsc="触发扩散反应8秒内，队友精通+50",
            elem_mastery=50,
        )

    def buff_T2(self, buff_info: BuffInfo, prop: DmgCalc):
        """小小的慧风"""
        elem_ma = prop.elem_mastery * 0.2
        buff_info.buff = Buff(
            dsc=f"风灵命中，基于砂糖精通，队友精通+{elem_ma}",
            elem_mastery=elem_ma,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """混元熵增论"""
        setting = buff_info.setting
        match setting.label:
            case x if x in ["火", "水", "雷", "冰"]:
                setting.state = f"{x}风"
                buff_info.buff.dsc = f"禁·风灵作成·柒伍同构贰型持续期间，{x}伤+20%"
                buff_info.buff.elem_dmg_bonus.set({x: 0.2})

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
        if self.info.ascension >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T1",
                    name="触媒置换术",
                    buff_range="party",
                    buff_type="propbuff",
                )
            )
            if self.info.ascension >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-T2",
                        name="小小的慧风",
                        buff_range="party",
                        buff_type="transbuff",
                    )
                )
        # 命座
        if self.info.constellation >= 6:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C6",
                    name="混元熵增论",
                    buff_range="all",
                    buff_type="propbuff",
                    setting=BuffSetting(
                        dsc="元素转化（火，水，雷，冰）：对应元素增伤+20%",
                        label=labels.get("混元熵增论", "火"),
                    ),
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "触媒置换术":
                    self.buff_T1(buff)
                case "小小的慧风":
                    self.buff_T2(buff)
                case "混元熵增论":
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

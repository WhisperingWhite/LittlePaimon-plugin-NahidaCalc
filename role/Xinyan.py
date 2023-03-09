from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, FixValue, Multiplier, PoFValue
from ..dmg_calc import DmgCalc
from ._model import Role


class Xinyan(Role):
    name = "辛焱"

    def buff_T2(self, buff_info: BuffInfo):
        """「这才是摇滚!」"""
        buff_info.buff = Buff(
            dsc="热情拂扫护盾下，物伤+15%",
            elem_dmg_bonus=DmgBonus(phy=0.15),
        )

    def buff_C2(self, buff_info: BuffInfo):
        """开场即兴段"""
        buff_info.buff = Buff(
            dsc="叛逆刮弦的物理伤害暴击率+100%",
            target="Q",
            crit_rate=1,
        )

    def buff_C4(self, buff_info: BuffInfo):
        """节奏的传染"""
        buff_info.buff = Buff(
            dsc="热情拂扫命中12秒内，物抗-15%",
            resist_reduction=DmgBonus(phy=0.15),
        )

    def buff_C6(self, buff_info: BuffInfo, prop: DmgCalc):
        """地狱里摇摆"""
        atk = prop.defense * 0.5
        buff_info.buff = Buff(
            dsc="重击时，基于防御力的50%获得攻击力(+)",
            atk=PoFValue(fix=atk),
        )

    def skill_E(self, dmg_info: Dmg):
        """热情拂扫"""
        calc = self.create_calc()
        scaler, fix_value = float(
            self.get_scaler("热情拂扫", self.talents[1].level, "三级护盾吸收量")
            .replace("%防御力", "")
            .split("+")
        )
        calc.set(
            multiplier=Multiplier(defense=scaler),
            fix_value=FixValue(shield=fix_value),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value = calc.calc_dmg.get_shield()

    def skill_Q(self, dmg_info: Dmg):
        """叛逆刮弦"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("叛逆刮弦", self.talents[2].level, "技能伤害").replace("%", "")
        )
        calc.set(
            value_type="Q",
            elem_type="phy",
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
        if self.info.ascension >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T2",
                    name="「这才是摇滚!」",
                    buff_range="active",
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="开场即兴段",
                )
            )
            if self.info.constellation >= 4:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C4",
                        name="节奏的传染",
                        buff_range="all",
                    )
                )
                if self.info.constellation >= 6:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C6",
                            name="地狱里摇摆",
                        )
                    )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "「这才是摇滚!」":
                    self.buff_T2(buff)
                case "开场即兴段":
                    self.buff_C2(buff)
                case "节奏的传染":
                    self.buff_C4(buff)
                case "地狱里摇摆":
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
                source="E",
                name="热情拂扫",
                value_type="S",
                dsc="E三级护盾",
                weight=weights.get("热情拂扫", 0),
                exclude_buff=ex_buffs.get("热情拂扫", []),
            ),
            Dmg(
                index=2,
                source="Q",
                name="叛逆刮弦",
                dsc="Q物理爆发",
                weight=weights.get("叛逆刮弦", 0),
                exclude_buff=ex_buffs.get("叛逆刮弦", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "热情拂扫":
                        self.skill_E(dmg)
                    case "叛逆刮弦":
                        self.skill_Q(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "热情拂扫": 10,
                    "叛逆刮弦": -1,
                }

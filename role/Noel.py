from ..classmodel import Buff, BuffInfo, Dmg, Multiplier, PoFValue
from ..dmg_calc import DmgCalc
from ._model import Role


class Noel(Role):
    name = "诺艾尔"

    def buff_C2(self, buff_info: BuffInfo):
        """旋风女仆"""
        buff_info.buff = Buff(
            dsc="重击增伤+15％",
            target="CA",
            hp=PoFValue(percent=0.2),
            defense=PoFValue(percent=0.2),
        )

    def buff_C6(self, buff_info: BuffInfo, prop: DmgCalc):
        """要一尘不染才行"""
        atk = prop.defense * 0.5
        buff_info.buff = Buff(
            dsc=f"大扫除额外攻击+50%防御({atk})",
            atk=PoFValue(fix=atk),
        )

    def skill_A(self, dmg_info: Dmg):
        """西风剑术·女仆"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("普通攻击•西风剑术·女仆", self.talents[0].level, "重击循环伤害").replace(
                "%", ""
            )
        )
        calc.set(
            value_type="CA",
            elem_type="geo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_Q(self, buff_info: BuffInfo, prop: DmgCalc):
        """大扫除"""
        scaler = float(
            self.get_scaler("大扫除", self.talents[2].level, "攻击力提高").replace("%防御力", "")
        )
        atk = prop.defense * scaler / 100
        buff_info.buff = Buff(
            dsc=f"基于防御，提高攻击+{atk}",
            atk=PoFValue(fix=atk),
        )

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict = {}) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="旋风女仆",
                )
            )
            if self.info.constellation >= 6:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C6",
                        name="要一尘不染才行",
                        buff_type="transbuff",
                    )
                )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="大扫除",
                buff_type="transbuff",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "旋风女仆":
                    self.buff_C2(buff)
                case "要一尘不染才行":
                    self.buff_C6(buff)
                case "大扫除":
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
                source="A",
                name="西风剑术·女仆",
                dsc="重击循环每段",
                weight=weights.get("西风剑术·女仆", 0),
                exclude_buff=ex_buffs.get("西风剑术·女仆", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "西风剑术·女仆":
                        self.skill_A(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "西风剑术·女仆": 10,
                }

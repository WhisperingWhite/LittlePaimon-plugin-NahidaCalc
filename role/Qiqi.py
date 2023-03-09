from ..classmodel import Buff, BuffInfo, Dmg, FixValue, Multiplier
from ._model import Role


class Qiqi(Role):
    name = "七七"

    def buff_T1(self, buff_info: BuffInfo):
        """延命妙法"""
        buff_info.buff = Buff(
            dsc="仙法·寒病鬼差状态下触发元素反应8秒内，受治疗加成+20%",
            healing=0.2,
        )

    def buff_C2(self, buff_info: BuffInfo):
        """冰寒蚀骨"""
        buff_info.buff = Buff(
            dsc="冰附着下，普攻与重击增伤+15%",
            target=["NA", "CA"],
            dmg_bonus=0.15,
        )

    def skill_E(self, dmg_info: Dmg):
        """仙法·寒病鬼差"""
        calc = self.create_calc()
        scaler, fix_value = float(
            self.get_scaler("仙法·寒病鬼差", self.talents[1].level, "持续治疗量")
            .replace("%攻击力", "")
            .split("+")
        )
        calc.set(
            value_type="H",
            multiplier=Multiplier(atk=scaler),
            fix_value=FixValue(heal=fix_value),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value = int(calc.calc_dmg.get_healing())

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
                    name="延命妙法",
                    buff_type="propbuff",
                )
            )
        # 命座
        if self.info.constellation >= 2:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C2",
                    name="冰寒蚀骨",
                )
            )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "延命妙法":
                    self.buff_T1(buff)
                case "冰寒蚀骨":
                    self.buff_C2(buff)

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
                name="仙法·寒病鬼差",
                dsc="E持续治疗",
                weight=weights.get("仙法·寒病鬼差", 0),
                exclude_buff=ex_buffs.get("仙法·寒病鬼差", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "仙法·寒病鬼差":
                        self.skill_E(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 200,
                    "仙法·寒病鬼差": 10,
                }

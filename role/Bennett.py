from ..classmodel import Dmg, Buff, BuffInfo, DmgBonus, Multiplier, FixValue, PoFValue
from ._model import Role


class Bennett(Role):
    name = "班尼特"

    def buff_C1(self, buff_info: BuffInfo):
        """冒险憧憬"""
        buff_info.buff = Buff(
            dsc="美妙旅程效果追加班尼特基础攻击力的20%",
        )

    def buff_C2(self, buff_info: BuffInfo):
        """踏破绝境"""
        buff_info.buff = Buff(
            dsc="生命值低于70％时，充能+30%",
            recharge=0.3,
        )

    def buff_C6(self, buff_info: BuffInfo):
        """烈火与勇气"""
        buff_info.buff = Buff(
            dsc="美妙旅程领域内，火伤+15%",
            elem_dmg_bonus=DmgBonus(pyro=0.15),
        )

    def buff_Q(self, buff_info: BuffInfo):
        """美妙旅程·鼓舞领域（增益）"""
        scaler = float(
            self.get_scaler("美妙旅程·鼓舞领域", self.talents[2].level, "攻击力加成比例").replace(
                "%", ""
            )
        )
        if self.info.constellation >= 1:
            scaler += 0.2
        atk = self.prop.atk_base * scaler
        buff_info.buff = Buff(
            dsc=f"鼓舞领域内，攻击+{atk}",
            atk=PoFValue(fix=atk),
        )

    def skill_Q_healing(self, dmg_info: Dmg):
        """美妙旅程·鼓舞领域（治疗）"""
        calc = self.create_calc()
        scaler, fix_value = float(
            self.get_scaler("美妙旅程", self.talents[2].level, "持续治疗")
            .replace("%生命值上限", "")
            .replace("每秒", "")
            .split("+")
        )
        calc.set(
            multiplier=Multiplier(hp=scaler),
            fix_value=FixValue(heal=fix_value),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value = calc.calc_dmg.get_healing()

    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 命座
        if self.info.constellation >= 1:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C1",
                    name="冒险憧憬",
                    buff_type="propbuff",
                )
            )
            if self.info.constellation >= 2:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C2",
                        name="踏破绝境",
                        buff_type="propbuff",
                    )
                )
                if self.info.constellation >= 6:
                    output.append(
                        BuffInfo(
                            source=f"{self.name}-C6",
                            name="烈火与勇气",
                            buff_range="active",
                            buff_type="propbuff",
                        )
                    )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="美妙旅程·鼓舞领域",
                buff_range="active",
                buff_type="propbuff",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "冒险憧憬":
                    self.buff_C1(buff)
                case "踏破绝境":
                    self.buff_C2(buff)
                case "烈火与勇气":
                    self.buff_C6(buff)
                case "美妙旅程·鼓舞领域":
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
                name="美妙旅程·鼓舞领域",
                value_type="H",
                dsc="Q治疗每秒",
                weight=weights.get("美妙旅程·鼓舞领域", 0),
                exclude_buff=ex_buffs.get("美妙旅程·鼓舞领域", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "美妙旅程·鼓舞领域":
                        self.skill_Q_healing(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "美妙旅程·鼓舞领域": 10,
                }

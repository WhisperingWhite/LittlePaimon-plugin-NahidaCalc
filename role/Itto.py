from ..classmodel import Buff, BuffInfo, Dmg, Multiplier, PoFValue
from ..dmg_calc import DmgCalc
from ._model import Role


class Itto(Role):
    name = "一斗"

    def buff_T2(self, buff_info: BuffInfo):
        """赤鬼之血"""
        buff_info.buff = Buff(
            dsc="荒泷逆袈裟倍率+35%防御力",
            target="CA",
            multiplier=Multiplier(defense=35),
        )

    def buff_C4(self, buff_info: BuffInfo, prop: DmgCalc):
        """奉行牢狱，茶饭之所"""
        buff_info.buff = Buff(
            dsc=f"怒目鬼王状态结束10秒内，全队防御+20%(+{prop.def_base*0.2})，攻击+20%(+{prop.hp_base*0.2}))",
            hp=PoFValue(percent=0.2),
            defense=PoFValue(percent=0.2),
        )

    def buff_C6(self, buff_info: BuffInfo):
        """在下荒泷一斗是也"""
        buff_info.buff = Buff(
            dsc="重击暴伤+70%",
            target="CA",
            crit_dmg=0.7,
        )

    def skill_A(self, dmg_info: Dmg):
        """喧哗屋传说"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("普通攻击•喧哗屋传说", self.talents[0].level, "荒泷逆袈裟连斩伤害").replace(
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

    def skill_E(self, dmg_info: Dmg):
        """魔杀绝技•赤牛发破！"""
        calc = self.create_calc()
        scaler = float(
            self.get_scaler("魔杀绝技•赤牛发破！", self.talents[1].level, "技能伤害").replace(
                "%", ""
            )
        )
        calc.set(
            value_type="E",
            elem_type="geo",
            multiplier=Multiplier(atk=scaler),
            exlude_buffs=dmg_info.exclude_buff,
        )
        dmg_info.exp_value, dmg_info.crit_value = calc.calc_dmg.get_dmg()

    def buff_Q(self, buff_info: BuffInfo, prop: DmgCalc):
        """最恶鬼王•一斗轰临！！"""
        scaler = float(
            self.get_scaler("最恶鬼王•一斗轰临！！", self.talents[2].level, "攻击力提高").replace(
                "%防御力", ""
            )
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
        # 天赋
        if self.info.ascension >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-T2",
                    name="赤鬼之血",
                )
            )
        # 命座
        if self.info.constellation >= 4:
            output.append(
                BuffInfo(
                    source=f"{self.name}-C4",
                    name="奉行牢狱，茶饭之所",
                    buff_range="all",
                    buff_type="propbuff",
                )
            )
            if self.info.constellation >= 6:
                output.append(
                    BuffInfo(
                        source=f"{self.name}-C6",
                        name="在下荒泷一斗是也",
                    )
                )
        # 技能
        output.append(
            BuffInfo(
                source=f"{self.name}-Q",
                name="最恶鬼王•一斗轰临！！",
                buff_type="transbuff",
            )
        )
        return output

    def buff(self, buff_list: list[BuffInfo], prop):
        """增益列表"""
        for buff in buff_list:
            match buff.name:
                case "赤鬼之血":
                    self.buff_T2(buff)
                case "奉行牢狱，茶饭之所":
                    self.buff_C4(buff)
                case "在下荒泷一斗是也":
                    self.buff_C6(buff)
                case "最恶鬼王•一斗轰临！！":
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
                name="喧哗屋传说",
                dsc="荒泷逆袈裟连斩",
                weight=weights.get("喧哗屋传说", 0),
                exclude_buff=ex_buffs.get("喧哗屋传说", []),
            ),
            Dmg(
                index=2,
                source="E",
                name="魔杀绝技•赤牛发破！",
                dsc="E投掷阿丑",
                weight=weights.get("魔杀绝技•赤牛发破！", 0),
                exclude_buff=ex_buffs.get("魔杀绝技•赤牛发破！", []),
            ),
        ]

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        for dmg in self.dmg_list:
            if dmg.weight != 0:
                match dmg.name:
                    case "喧哗屋传说":
                        self.skill_A(dmg)
                    case "魔杀绝技•赤牛发破！":
                        self.skill_E(dmg)
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {
                    "充能效率阈值": 100,
                    "喧哗屋传说": 10,
                    "魔杀绝技•赤牛发破！": -1,
                }

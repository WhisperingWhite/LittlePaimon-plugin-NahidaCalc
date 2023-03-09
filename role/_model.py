from nonebot.utils import run_sync
from asyncio import run
from LittlePaimon.database import (
    Artifacts,
    Character,
    CharacterProperty,
    Talents,
    Weapon,
)
from LittlePaimon.utils.files import load_json
from LittlePaimon.utils.genshin import GenshinTools
from LittlePaimon.utils.path import JSON_DATA

from ..classmodel import BuffInfo, Dmg, DmgBonus, Info, Buff
from ..dmg_calc import DmgCalc
from ..relics import artifacts, artifacts_setting
from ..resonance import resonance, resonance_setting
from ..weapon import weapon_buff, weapon_setting


class Calculator(DmgCalc):
    """角色内部使用伤害计算器"""

    buffs: list[BuffInfo] = []
    """增益"""

    def __init__(
        self,
        prop: CharacterProperty,
        level=90,
    ) -> None:
        super().__init__(prop, level)

    def update_buff(self, buffs: list[BuffInfo]):
        self.buffs = buffs
        return self

    @property
    def propbuff(self):
        """面板型增益"""
        return [buff for buff in self.buffs if buff.buff_type == "propbuff"]

    @property
    def transbuff(self):
        """面板型增益"""
        return [buff for buff in self.buffs if buff.buff_type == "transbuff"]

    @property
    def dmgbuff(self):
        """面板型增益"""
        return [buff for buff in self.buffs if buff.buff_type == "dmgbuff"]

    @property
    def calc_prop(self):
        """
        叠加propbuff后的面板
        """
        return self + self.propbuff

    @property
    def calc_trans(self):
        """
        叠加transbuff后的面板
        """
        return self.calc_prop + self.transbuff

    @property
    def calc_dmg(self):
        """
        战斗实时面板
        """
        return self.calc_trans + self.dmgbuff


class Role:
    """
    角色计算模型(非实例化)
    """

    name: str = ""
    """角色名称"""
    artifacts: Artifacts
    """圣遗物"""
    weapon: Weapon
    """武器"""
    prop: Calculator
    """纯面板属性"""
    talents: Talents
    """天赋"""
    scaler_table: dict
    """倍率表"""
    info: Info
    """杂项信息"""

    def __init__(self, charc: Character = None) -> None:
        if charc:
            self.artifacts = charc.artifacts
            self.weapon = charc.weapon
            self.prop = Calculator(charc.prop, charc.level)
            self.talents = charc.talents
            self.scaler_table = (
                load_json(JSON_DATA / "roles_data.json")
                .get(self.name, {})
                .get("skill", [])
            )
            self.info = Info(
                level=charc.level,
                element=charc.element,
                # constellation=len(charc.constellation.constellation_list),
                constellation=6,
                # ascension = charc.promote_level,
                ascension=6,
                suit=get_relicsuit(charc.artifacts),
                region=charc.region,
                weapon_type=charc.weapon.type,
            )

    def get_scaler(self, skill_name: str, skill_level: int, *attributes: str):
        """获取倍率"""
        output: list[str] = []
        table_ = self.scaler_table[skill_name]["数值"]
        for attr in attributes:
            output.append(table_[attr][skill_level - 1])
        if len(output) == 0:
            return 0
        if len(output) == 1:
            return output[0]
        return output

    partner: list["Role"] = []
    """队友模型"""

    def get_partner(self, list: list["Role"]):
        """获取队友"""
        self.partner = list[0:3]

    resonance: str = ""
    """元素共鸣"""

    buffs: list[BuffInfo] = []
    """增益"""
    dmg_list: list[Dmg] = []
    """伤害"""

    def create_calc(self):
        """创建一个伤害计算器"""
        return self.prop.copy().update_buff(self.buffs)

    category: str = ""
    """角色所属的流派，影响圣遗物分数计算"""
    @property
    def valid_prop(self) -> list[str]:
        """有效属性"""
        return []

    def setting(self, labels: dict) -> list[BuffInfo]:
        """增益设置"""
        output: list[BuffInfo] = []
        # 天赋
        # 命座
        return output

    def buff(self, buff_list: list[BuffInfo], prop: DmgCalc):
        """增益列表"""

    def weight(self, weights: dict, ex_buffs: dict):
        """伤害权重"""
        self.dmg_list = []

    def dmg(self) -> list[Dmg]:
        """伤害列表"""
        return self.dmg_list

    def weights_init(self, style_name: str = "") -> dict[str, int]:
        """角色出伤流派"""
        match style_name:
            case _:
                return {}

    @run_sync
    def update_setting(self, labels: dict[str, str] = {}):
        """
        获取人物增益设定
        """
        self.buffs = []
        # 共鸣增益设置
        self.buffs.extend(resonance_setting(self.resonance, labels))
        # 天赋、命座增益设置
        self.buffs.extend(self.setting(labels))
        # 武器增益设置
        self.buffs.extend(weapon_setting(self.weapon, self.info, labels, self.name))
        # 圣遗物增益设置
        self.buffs.extend(artifacts_setting(self.info.suit, labels, self.name))
        # 队友增益设置
        for p in self.partner:
            run(p.update_setting(labels))
            self.buffs.extend(p.get_party_buffs())
        return self.buffs

    @run_sync
    def update_buff(self):
        """
        获取人物增益
        更新增益列表并且返回团队增益
        """
        # 队友增益设置
        for p in self.partner:
            p.update_buff()
            self.buffs.extend(p.get_party_buffs())
        # 命座、天赋和技能增益
        for buff_type in ["propbuff", "transbuff", "dmgbuff"]:
            prop = self.create_calc()
            match buff_type:
                case "propbuff":
                    input_buff = [
                        buff
                        for buff in prop.propbuff
                        if buff.buff_range != "party" or self.name not in buff.source
                    ]
                    calc = prop
                case "transbuff":
                    input_buff = [
                        buff
                        for buff in prop.transbuff
                        if buff.buff_range != "party" or self.name not in buff.source
                    ]
                    calc = prop.calc_prop
                case "dmgbuff":
                    input_buff = [
                        buff
                        for buff in prop.dmgbuff
                        if buff.buff_range != "party" or self.name not in buff.source
                    ]
                    calc = prop.calc_trans
            # 共鸣增益
            resonance(input_buff, calc)
            # 天赋、命座增益
            self.buff(input_buff, calc)
            # 武器增益
            weapon_buff(self.weapon, input_buff, self.info, calc)
            # 圣遗物增益
            artifacts(input_buff, self.info, calc)
        return self.buffs

    @run_sync
    def update_dmg(
        self, weights: dict[str, int] = {}, ex_buffs: dict[str, list[str]] = {}
    ):
        """获取伤害列表"""
        # if weights == {}:
        weights = self.weights_init()
        self.weight(weights, ex_buffs)
        return self.dmg()

    def get_party_buffs(self):
        output_buff: list[BuffInfo] = []
        for buff in self.buffs:
            if buff.buff_range != "self":
                output_buff.append(buff)
        return output_buff

    def setting_conduct(self, labels: dict):
        """超导设置"""
        return BuffInfo(
            source="元素反应",
            name="超导",
        )

    def buff_conduct(self, buff_info: BuffInfo):
        """超导增益"""
        buff_info.buff = Buff(
            dsc="冰雷反应触发12秒内，物抗-40%",
            resist_reduction=DmgBonus(phy=0.4),
        )


def reserve_setting(buff_list: list[BuffInfo]):
    """保留设置"""
    labels: dict[str, str] = {}
    for buff in buff_list:
        labels |= {buff.name: buff.setting.label}
    return labels


def reserve_weight(dmg_list: list[Dmg]):
    """保留权重"""
    weights: dict[str, int] = {}
    for dmg in dmg_list:
        weights |= {dmg.name: dmg.weight}
    return weights


def reserve_exbuffs(dmg_list: list[Dmg]):
    """保留无效增益"""
    ex_buffs: dict[str, int] = {}
    for dmg in dmg_list:
        ex_buffs |= {dmg.name: dmg.exclude_buff}
    return ex_buffs


def get_relicsuit(relics: Artifacts):
    output: dict[str, int] = {}
    for suit, _ in GenshinTools.get_artifact_suit(relics):
        output.update({suit: output.get(suit, 0) + 2})
    return output

import typing
from asyncio import run

from nonebot.utils import run_sync

from LittlePaimon.database import (
    Artifacts,
    Character,
    CharacterProperty,
    Talents,
    Weapon,
)
from LittlePaimon.utils.alias import get_match_alias
from LittlePaimon.utils.files import load_json
from LittlePaimon.utils.path import JSON_DATA

from ..classmodel import Buff, BuffInfo, Dmg, DmgBonus, Info, RelicScore
from ..dmg_calc import DmgCalc
from ..Nahidatools import (
    get_relicsuit,
    reserve_exbuffs,
    reserve_setting,
    reserve_weight,
)
from ..relics import artifacts, artifacts_setting
from ..resonance import resonance, resonance_setting
from ..score import get_scores
from ..weapon import weapon_buff, weapon_setting

if typing.TYPE_CHECKING:
    from ..database import CalcInfo


class Calculator(DmgCalc):
    """角色内部使用伤害计算器"""

    buffs: list[BuffInfo] = []
    """增益"""

    def __init__(
        self,
        prop: CharacterProperty,
        level=90,
    ) -> None:
        if prop:
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

    def __init__(self, charc: Character = None, data: "CalcInfo" = None) -> None:
        if charc:
            self.artifacts = charc.artifacts
            self.weapon = charc.weapon
            self.prop = Calculator(charc.prop, charc.level)
            self.talents = charc.talents
            self.scaler_table = (
                load_json(JSON_DATA / "roles_data.json")
                .get(charc.name, {})
                .get("skill", [])
            )
            self.info = Info(
                level=charc.level,
                element=charc.element,
                constellation=len(charc.constellation),
                # constellation=6,
                ascension=charc.promote_level,
                # ascension=6,
                suit=get_relicsuit(charc.artifacts),
                region=charc.region,
                weapon_type=charc.weapon.type,
            )
            if data:
                self.buffs = data.buffs
                self.dmg_list = data.dmgs
                self.partners = data.strToRole()
                self.resonance = data.resonance
                if data.category != "":
                    self.category = data.category

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

    partners: list["Role"] = []
    """队友名单"""

    def get_partner(self) -> list["Role"]:
        """获取队友"""
        output = []
        for p in self.partners[:3]:
            output.extend(get_match_alias(p, "角色"))
        return output

    resonance: str = ""
    """元素共鸣"""

    buffs: list[BuffInfo] = []
    """增益"""
    dmg_list: list[Dmg] = []
    """伤害"""
    scores: RelicScore = RelicScore()
    """圣遗物评分"""

    def create_calc(self):
        """创建一个伤害计算器"""
        return self.prop.copy().update_buff(self.buffs)

    @property
    def calc_recharge(self):
        """圣遗物计算用充能"""
        calc = self.create_calc() + [
            buff for buff in self.buffs if buff.source == "calc"
        ]
        return calc.recharge

    category: str = ""
    """角色所属的流派，影响圣遗物分数计算"""
    cate_list: list[str] = []
    """可选流派"""

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

    def weights_init(self) -> dict[str, int]:
        """角色出伤流派"""
        match self.category:
            case _:
                return {}

    @run_sync
    def update_setting(self, labels: dict[str, str] = {}, old_buffs: list = None):
        """
        获取人物增益设定
        """
        if old_buffs is None:
            labels = reserve_setting(self.buffs)
        else:
            labels = reserve_setting(old_buffs)
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
        for p in self.partners:
            run(p.update_setting(labels, old_buffs))
            self.buffs.extend(p.get_party_buffs())
        return self.buffs

    @run_sync
    def update_buff(self):
        """
        获取人物增益
        更新增益列表并且返回团队增益
        """
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
            # 队友增益
            for p in self.partners:
                p.buff(input_buff, calc)
        return self.buffs

    @run_sync
    def update_dmg(self, is_new: bool = False):
        """获取伤害列表"""
        if is_new:
            weights = self.weights_init()
        else:
            weights = reserve_weight(self.dmg_list)
        ex_buffs = reserve_exbuffs(self.dmg_list)
        self.weight(weights, ex_buffs)
        return self.dmg()

    @run_sync
    def update_scores(self):
        """获取圣遗物评分"""
        self.scores = get_scores(self)
        return self.scores

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

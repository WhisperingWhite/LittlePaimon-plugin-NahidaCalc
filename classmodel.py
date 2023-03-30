from pydantic import BaseModel, parse_raw_as
import json


class DmgBonus(BaseModel):
    """伤害加成/元素抗性"""

    phy: float = 0.0
    """物理伤害加成"""
    pyro: float = 0.0
    """火元素伤害加成"""
    electro: float = 0.0
    """雷元素伤害加成"""
    hydro: float = 0.0
    """水元素伤害加成"""
    dendro: float = 0.0
    """草元素伤害加成"""
    anemo: float = 0.0
    """风元素伤害加成"""
    geo: float = 0.0
    """岩元素伤害加成"""
    cryo: float = 0.0
    """冰元素伤害加成"""

    def __add__(self, other: "DmgBonus"):
        return DmgBonus(
            phy=self.phy + other.phy,
            pyro=self.pyro + other.pyro,
            electro=self.electro + other.electro,
            hydro=self.hydro + other.hydro,
            dendro=self.dendro + other.dendro,
            anemo=self.anemo + other.anemo,
            geo=self.geo + other.geo,
            cryo=self.cryo + other.cryo,
        )

    def __sub__(self, other: "DmgBonus"):
        return DmgBonus(
            phy=self.phy - other.phy,
            pyro=self.pyro - other.pyro,
            electro=self.electro - other.electro,
            hydro=self.hydro - other.hydro,
            dendro=self.dendro - other.dendro,
            anemo=self.anemo - other.anemo,
            geo=self.geo - other.geo,
            cryo=self.cryo - other.cryo,
        )

    def get(self, key: str):
        match key:
            case x if x in ["物理", "phy", "物伤"]:
                return self.phy
            case x if x in ["火", "pyro", "火伤"]:
                return self.pyro
            case x if x in ["雷", "electro", "雷伤"]:
                return self.electro
            case x if x in ["水", "hydro", "水伤"]:
                return self.hydro
            case x if x in ["草", "dendro", "草伤"]:
                return self.dendro
            case x if x in ["风", "anemo", "风伤"]:
                return self.anemo
            case x if x in ["岩", "geo", "岩伤"]:
                return self.geo
            case x if x in ["冰", "cryo", "冰伤"]:
                return self.cryo
            case _:
                return 0.0

    def set(self, dmgprops: dict):
        for key, value in dmgprops.items():
            match key:
                case x if x in ["物理", "phy", "物伤"]:
                    self.phy = value
                case x if x in ["火", "pyro", "火伤"]:
                    self.pyro = value
                case x if x in ["雷", "electro", "雷伤"]:
                    self.electro = value
                case x if x in ["水", "hydro", "水伤"]:
                    self.hydro = value
                case x if x in ["草", "dendro", "草伤"]:
                    self.dendro = value
                case x if x in ["风", "anemo", "风伤"]:
                    self.anemo = value
                case x if x in ["岩", "geo", "岩伤"]:
                    self.geo = value
                case x if x in ["冰", "cryo", "冰伤"]:
                    self.cryo = value
                case x if x in ["元素", "elem"]:
                    for k in ["火", "雷", "水", "草", "风", "岩", "冰"]:
                        self.set({k: value})
                case "all":
                    self.set({"elem": value})
                    self.phy = value
        return self


class Multiplier(BaseModel):
    """倍率"""

    atk: float = 0.0
    """基于攻击"""
    hp: float = 0.0
    """基于生命"""
    defense: float = 0.0
    """基于防御"""
    em: float = 0.0
    """基于精通"""

    def __add__(self, other: "Multiplier"):
        return Multiplier(
            atk=self.atk + other.atk,
            hp=self.hp + other.hp,
            defense=self.defense + other.defense,
            em=self.em + other.em,
        )


class PoFValue(BaseModel):
    """三围增益"""

    percent: float = 0.0
    fix: float = 0.0

    def __add__(self, other: "PoFValue"):
        return PoFValue(
            percent=self.percent + other.percent,
            fix=self.fix + other.fix,
        )


class FixValue(BaseModel):
    """固值增益"""

    dmg: float = 0.0
    heal: float = 0.0
    shield: float = 0.0

    def __add__(self, other: "FixValue"):
        return FixValue(
            dmg=self.dmg + other.dmg,
            heal=self.heal + other.heal,
            shield=self.shield + other.shield,
        )


class ReaFactor(BaseModel):
    """反应系数"""

    vaporize: float = 0.0
    """蒸发"""
    melt: float = 0.0
    """融化"""
    spread: float = 0.0
    """蔓激化"""
    aggravate: float = 0.0
    """超激化"""
    burning: float = 0.0
    """燃烧"""
    overloaded: float = 0.0
    """超载"""
    charged: float = 0.0
    """感电"""
    shatter: float = 0.0
    """碎冰"""
    conduct: float = 0.0
    """超导"""
    bloom: float = 0.0
    """原绽放"""
    burgeon: float = 0.0
    """烈绽放"""
    hyperbloom: float = 0.0
    """超绽放"""
    swirl: float = 0.0
    """扩散"""
    crystallize: float = 0.0
    """结晶"""

    def __add__(self, other: "ReaFactor"):
        return ReaFactor(
            vaporize=self.vaporize + other.vaporize,
            melt=self.melt + other.melt,
            spread=self.spread + other.spread,
            aggravate=self.aggravate + other.aggravate,
            burning=self.burning + other.burning,
            overloaded=self.overloaded + other.overloaded,
            charged=self.charged + other.charged,
            shatter=self.shatter + other.shatter,
            conduct=self.conduct + other.conduct,
            bloom=self.bloom + other.bloom,
            burgeon=self.burgeon + other.burgeon,
            hyperbloom=self.hyperbloom + other.hyperbloom,
            swirl=self.swirl + other.swirl,
            crystallize=self.crystallize + other.crystallize,
        )

    def init(self):
        """角色初始化"""
        self.vaporize = 1
        self.melt = 1
        self.spread = 1
        self.aggravate = 1
        self.burning = 1
        self.overloaded = 1
        self.charged = 1
        self.shatter = 1
        self.conduct = 1
        self.bloom = 1
        self.burgeon = 1
        self.hyperbloom = 1
        self.swirl = 1
        self.crystallize = 1
        return self

    def get(self, reaction_type: str):
        match reaction_type:
            case "蒸发":
                return self.vaporize
            case "融化":
                return self.melt
            case "蔓激化":
                return self.spread
            case "超激化":
                return self.aggravate
            case "燃烧":
                return self.burning
            case "超载":
                return self.overloaded
            case "感电":
                return self.charged
            case "碎冰":
                return self.shatter
            case "超导":
                return self.conduct
            case "原绽放":
                return self.bloom
            case "烈绽放":
                return self.burgeon
            case "超绽放":
                return self.hyperbloom
            case "扩散":
                return self.swirl
            case "结晶":
                return self.crystallize


class Buff(BaseModel):
    """增益器"""

    dsc: str = ""
    """增益描述"""
    target: list[str] | str = "ALL"
    """增益目标：\\
        NA-普通攻击\\
        CA-重击\\
        PA-下落攻击\\
        E-元素战技\\
        Q-元素爆发\\
        ALL-所有类型\\
        H-治疗\\
        S-护盾
    """
    # elem_type: str | list[str] = "all"
    # """伤害元素类型：\\
    #     phy-物理\\
    #     pyro-火属性\\
    #     electro-雷属性\\
    #     hydro-水属性\\
    #     dendro-草属性\\
    #     anemo-风属性\\
    #     geo-岩属性\\
    #     cryo-冰属性\\
    #     all-所有类型\\
    #     elem-元素增伤
    # """
    # triger_type: str = "all"
    # """触发类型：\\
    #     all-均可触发或无关\\
    #     active-场上触发\\
    #     off field-后台触发
    # """
    # reaction_type: str | list[str] = ""
    # """元素反应类型：\\
    #     剧变："燃烧", "超导", "扩散", "感电", "碎冰", "超载", "原绽放", "烈绽放", "超绽放", "结晶"\\
    #     增幅："火蒸发", "冰融化", "水蒸发", "火融化", "蔓激化", "超激化"
    # """
    hp: PoFValue = PoFValue()
    """生命增益"""
    atk: PoFValue = PoFValue()
    """攻击增益"""
    defense: PoFValue = PoFValue()
    """防御增益"""
    multiplier: Multiplier = Multiplier()
    """倍率增益"""
    crit_rate: float = 0.0
    """暴击增益"""
    crit_dmg: float = 0.0
    """暴伤增益"""
    elem_mastery: float = 0.0
    """精通增益"""
    recharge: float = 0.0
    """充能增益"""
    elem_dmg_bonus: DmgBonus = DmgBonus()
    """元素伤害加成增益"""
    healing: float = 0.0
    """治疗加成增益"""
    shield_strength: float = 0.0
    """护盾强效"""
    dmg_bonus: float = 0.0
    """增伤增益"""
    resist_reduction: DmgBonus = DmgBonus()
    """减抗"""
    def_reduction: float = 0.0
    """减防"""
    def_piercing: float = 0.0
    """无视防御"""
    fix_value: FixValue = FixValue()
    """固值加成"""
    reaction_coeff: ReaFactor = ReaFactor()
    """反应系数增益"""


class BuffSetting(BaseModel):
    """
    增益设置
    """

    dsc: str = "此增益为常驻增益，⓪关①开"
    """描述"""
    label: str = "○"
    """设置"""
    state: str = "✓"
    """状态"""


class BuffInfo(BaseModel):
    """增益列表"""

    source: str = ""
    """增益来源"""
    name: str = ""
    """增益名"""
    buff_range: str = "self"
    """加成范围：\\
        self-自身\\
        party-其余友方成员\\
        all-全部队伍成员、场上成员
    """
    buff_type: str = "dmgbuff"
    """增益类型：\\
            propbuff-面板型增益
            transbuff-转移型增益
            dmgbuff-伤害型增益
    """
    duration: int = 0
    """持续时间"""
    buff: Buff = Buff()
    """增益器"""
    setting: BuffSetting = BuffSetting()
    """增益器设置"""


class Dmg(BaseModel):
    """伤害表"""

    index: int
    """序号"""
    source: str = ""
    """数值来源"""
    name: str = ""
    """技能名称"""
    value_type: str = "D"
    """类型：
        D：伤害
        H：治疗
        S：护盾
        B：增益
    """
    dsc: str = ""
    """描述"""
    exp_value: int = 0
    """期望伤害"""
    crit_value: int = 0
    """暴击伤害"""
    weight: int = 0
    """权重 -1-10"""
    exclude_buff: list[str] = []
    """无效增益"""


class Info(BaseModel):
    """杂项信息"""

    level: int = 90
    """等级"""
    element: str
    """神之眼"""
    constellation: int = 0
    """命之座"""
    ascension: int = 6
    """突破"""
    suit: dict = {}
    """圣遗物套装"""
    region: str = ""
    """地区"""
    weapon_type: str = ""
    """武器类型"""


class BuffList(BaseModel):
    @classmethod
    def encode(cls, models: list["BuffInfo"]):
        return json.dumps(models, default=cls.dict)

    @classmethod
    def decode(cls, json_data):
        return parse_raw_as(list[BuffInfo], json_data)


class DmgList(BaseModel):
    @classmethod
    def encode(cls, models: list["Dmg"]):
        return json.dumps(models, default=cls.dict)

    @classmethod
    def decode(cls, json_data):
        return parse_raw_as(list[Dmg], json_data)


class RelicScore(BaseModel):
    """
    圣遗物评分
    """

    flower: float = -1
    """生之花"""
    plume: float = -1
    """死之羽"""
    sands: float = -1
    """时之沙"""
    goblet: float = -1
    """空之杯"""
    circlet: float = -1
    """理之冠"""

    @property
    def total_score(self) -> float:
        """圣遗物总分"""
        score = 0
        for s in [self.flower, self.plume, self.sands, self.goblet, self.circlet]:
            score += s if s != -1 else 0
        return score

    def get_score(self, key="total"):
        match key:
            case "生之花":
                return self.flower
            case "死之羽":
                return self.plume
            case "时之沙":
                return self.sands
            case "空之杯":
                return self.goblet
            case "理之冠":
                return self.circlet
            case "total":
                return self.total_score

    def set_score(self, key, value):
        match key:
            case "生之花":
                self.flower = value
            case "死之羽":
                self.plume = value
            case "时之沙":
                self.sands = value
            case "空之杯":
                self.goblet = value
            case "理之冠":
                self.circlet = value

    @classmethod
    def decode(cls, json_data):
        return parse_raw_as(RelicScore, json_data)

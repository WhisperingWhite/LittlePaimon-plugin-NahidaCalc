from tortoise import fields
from tortoise.models import Model

from LittlePaimon.database import Character
from LittlePaimon.utils.genshin import GenshinInfoManager

from ..classmodel import BuffInfo, BuffList, Dmg, DmgList, RelicScore
from ..role import get_role
from asyncio import run


class CalcInfo(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    user_id: str = fields.CharField(max_length=15)
    """用户id"""
    uid: str = fields.CharField(max_length=10)
    """原神uid"""
    name: str = fields.CharField(max_length=32)
    """角色名"""
    buffs: list[BuffInfo] = fields.JSONField(
        encoder=BuffList.encode, decoder=BuffList.decode, default=[]
    )
    """增益"""
    dmgs: list[Dmg] = fields.JSONField(
        encoder=DmgList.encode, decoder=DmgList.decode, default=[]
    )
    """伤害"""
    scores: RelicScore = fields.JSONField(
        encoder=RelicScore.json, decoder=RelicScore.parse_raw, default=RelicScore()
    )
    """圣遗物分数"""
    partner: list = fields.JSONField(default=[])
    """队友"""
    category: str = fields.CharField(max_length=10, default="")
    """伤害流派"""
    resonance: str = fields.CharField(max_length=10, default="")
    """元素共鸣"""
    valid_prop: list = fields.JSONField(default=[])
    """有效属性"""
    update_time = fields.DatetimeField(auto_now=True)
    """更新时间"""

    @classmethod
    async def update(cls, user_id: str, uid: str, charc: Character):
        calc_info, is_new = await cls.get_or_create(
            user_id=user_id, uid=uid, name=charc.name
        )
        role = get_role(charc, calc_info)
        await role.update_setting(calc_info.buffs)
        calc_info.buffs = await role.update_buff()
        calc_info.dmgs = await role.update_dmg(is_new)
        calc_info.scores = await role.update_scores()
        (
            calc_info.partner,
            calc_info.category,
            calc_info.valid_prop,
            calc_info.resonance,
        ) = (role.get_partner(), role.category, role.valid_prop, role.resonance)
        await calc_info.save()

    def strToRole(cls):
        """把角色名称转换成相应模型"""
        output_list = []
        for partn in cls.partner[:3]:
            gim = GenshinInfoManager(cls.user_id, cls.uid)
            charc = run(gim.get_character(name=partn, data_source="enka"))
            output_list.append(get_role(charc))
        return output_list

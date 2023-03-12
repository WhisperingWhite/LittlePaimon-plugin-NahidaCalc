from tortoise import fields
from tortoise.models import Model
from ..classmodel import DmgList, BuffList, RelicScore
from ..role import Role
from ..Nahidatools import reserve_exbuffs, reserve_setting, reserve_weight
from ..score import get_scores


class Data(Model):
    id = fields.IntField(pk=True, generated=True, auto_increment=True)
    user_id: str = fields.CharField(max_length=15)
    """用户id"""
    uid: str = fields.CharField(max_length=10)
    """原神uid"""
    name: str = fields.CharField(max_length=32)
    """角色名"""
    buffs: BuffList = fields.JSONField(
        encoder=BuffList.encode, decoder=BuffList.decode, default=[]
    )
    """增益"""
    dmgs: DmgList = fields.JSONField(
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
    valid_prop: list = fields.JSONField(default=[])
    """有效属性"""

    @classmethod
    async def update(cls, user_id: str, uid: str, name: str, role: Role):
        chara, is_new = await cls.get_or_create(user_id=user_id, uid=uid, name=name)
        if is_new:
            role.partner, role.category = chara.partner, chara.category
            weights = role.weights_init()
        else:
            weights = reserve_weight(chara.dmgs)
        await role.update_setting(reserve_setting(chara.buffs))
        chara.buffs = await role.update_buff()
        chara.dmgs = await role.update_dmg(weights, reserve_exbuffs(chara.dmgs))
        chara.scores = await get_scores(role)
        chara.partner, chara.category, chara.valid_prop = role.partner, role.category, role.valid_prop
        await chara.save()

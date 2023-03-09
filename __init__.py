from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from LittlePaimon.database import PlayerAlias, LastQuery
from LittlePaimon.utils import logger

from LittlePaimon.utils.message import CommandPlayer, CommandCharacter
from LittlePaimon.utils.genshin import GenshinInfoManager
from .role import get_role
from .score import get_scores

test = on_command(
    "test",
    priority=10,
    block=True,
    state={
        "pm_name": "test",
        "pm_description": "查看指定角色的详细面板数据及伤害计算",
        "pm_usage": "test(uid)<角色名>",
        "pm_priority": 5,
    },
)


@test.handle()
async def _(
    event: MessageEvent,
    players=CommandPlayer(only_cn=False),
    characters=CommandCharacter(),
):
    logger.info("Nahida面板", "开始执行")
    msg = ""
    # msg = Message()
    try:
        if len(players) == 1:
            # 当查询对象只有一个时，查询所有角色
            gim = GenshinInfoManager(players[0].user_id, players[0].uid)
            await LastQuery.update_last_query(players[0].user_id, players[0].uid)
            logger.info(
                "Nahida面板", "➤", {"用户": players[0].user_id, "UID": players[0].uid}
            )
            for character in characters:
                character_info = await gim.get_character(
                    name=character, data_source="enka"
                )
                if character_info:
                    role = get_role(character_info)
                    setting = await role.update_setting()
                    buff = await role.update_buff()
                    dmg = await role.update_dmg()
                    scores = await get_scores(role)
                    msg = f"{role.name}已更新"
    except KeyError as e:
        msg = f"获取角色信息失败，缺少{e}的数据，可能是Enka.Network接口出现问题"
    except Exception as e:
        msg = f"获取角色信息失败，错误信息：{e}"
    await test.finish(msg, at_sender=True)

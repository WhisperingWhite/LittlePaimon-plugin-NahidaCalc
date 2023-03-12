from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from LittlePaimon.database import LastQuery
from LittlePaimon.utils import DRIVER, logger
from LittlePaimon.utils.genshin import GenshinInfoManager
from LittlePaimon.utils.message import CommandCharacter, CommandPlayer

from .database import Data, connect, disconnect
from .draw_character_detail import draw_chara_detail
from .role import get_role

DRIVER.on_startup(connect)
DRIVER.on_shutdown(disconnect)

update = on_command(
    "upd",
    aliases={"nhd更新"},
    priority=9,
    block=True,
    state={
        "pm_name": "upd",
        "pm_description": '更新你的原神玩家和角色数据，绑定cookie后数据更详细，加上"天赋"可以更新天赋等级',
        "pm_usage": "nhd更新<角色名>",
        "pm_priority": 1,
    },
)


@update.handle()
async def _(
    event: MessageEvent,
    players=CommandPlayer(only_cn=False),
    characters=CommandCharacter(),
):
    logger.info("Nahida面板", "数据更新")
    user_id, uid = players[0].user_id, players[0].uid
    try:
        gim = GenshinInfoManager(user_id, uid)
        # await LastQuery.update_last_query(user_id, uid)
        logger.info("Nahida面板", "➤", {"用户": user_id, "UID": uid})
        for character in characters:
            character_info = await gim.get_character(name=character, data_source="enka")
            if character_info:
                role = get_role(character_info)
                await Data.update(user_id, uid, character_info.name, role)
                logger.success("Nahida面板", f"{role.name}更新成功")
                msg = f"{role.name}已更新"
    except KeyError as e:
        msg = f"获取角色信息失败，缺少{e}的数据，可能是Enka.Network接口出现问题"
    except Exception as e:
        msg = f"获取角色信息失败，错误信息：{e}"
    await update.finish(msg, at_sender=True)


clear = on_command(
    "clear",
    aliases={"nhd重置"},
    priority=9,
    block=True,
    state={
        "pm_name": "clear",
        "pm_description": '更新你的原神玩家和角色数据，绑定cookie后数据更详细，加上"天赋"可以更新天赋等级',
        "pm_usage": "nhd重置",
        "pm_priority": 2,
    },
)


@clear.handle()
async def _(
    event: MessageEvent,
    players=CommandPlayer(only_cn=False),
):
    user_id, uid = players[0].user_id, players[0].uid
    logger.info("Nahida面板", f"清除{players[0].uid}数据")
    await Data.filter(user_id=user_id, uid=uid).delete()
    await clear.finish("已成功清除", at_sender=True)


nhd = on_command(
    "nhd",
    priority=10,
    block=True,
    state={
        "pm_name": "nhd",
        "pm_description": "查看指定角色的详细面板数据及伤害计算",
        "pm_usage": "nhd(uid)<角色名>",
        "pm_priority": 3,
    },
)


@nhd.handle()
async def _(
    event: MessageEvent,
    players=CommandPlayer(only_cn=False),
    characters=CommandCharacter(),
):
    logger.info("Nahida面板", "开始执行")
    msg = Message()
    # msg = Message()
    user_id, uid = players[0].user_id, players[0].uid
    try:
        if len(players) == 1:
            # 当查询对象只有一个时，查询所有角色
            gim = GenshinInfoManager(user_id, uid)
            # await LastQuery.update_last_query(user_id, uid)
            logger.info("Nahida面板", "➤", {"用户": user_id, "UID": uid})
            for character in characters:
                character_info = await gim.get_character(
                    name=character, data_source="enka"
                )
                if not character_info:
                    logger.info("Nahida面板", "➤➤", {"角色": character}, "没有该角色信息", False)
                    msg = f"\n暂无你{character}信息，请在游戏内展柜放置该角色"
                else:
                    data = await Data.filter(
                        user_id=user_id, uid=uid, name=character_info.name
                    ).first()
                    if data is None:
                        role = get_role(character_info)
                        await Data.update(user_id, uid, character_info.name, role)
                        data = await Data.filter(
                            user_id=user_id, uid=uid, name=character_info.name
                        ).first()
                    img = await draw_chara_detail(uid, character_info, data)
                    logger.info("Nahida面板", "➤➤➤", {}, "制图完成", True)
                    msg += img
        else:
            # 当查询对象有多个时，只查询第一个角色
            for player in players:
                gim = GenshinInfoManager(player.user_id, player.uid)
                # await LastQuery.update_last_query(player.user_id, player.uid)
                logger.info("原神角色面板", "➤", {"用户": player.user_id, "UID": player.uid})
                character_info = await gim.get_character(
                    name=characters[0], data_source="enka"
                )
                if not character_info:
                    msg += f"\n暂无{player.uid}的{characters[0]}信息，请在游戏内展柜放置该角色"
                else:
                    img = await draw_chara_detail(player.uid, character_info)
                    logger.info("原神角色面板", "➤➤➤", {}, "制图完成", True)
                    msg += img
    except KeyError as e:
        msg = f"获取角色信息失败，缺少{e}的数据，可能是Enka.Network接口出现问题"
    except Exception as e:
        msg = f"获取角色信息失败，错误信息：{e}"
    await nhd.finish(msg, at_sender=True)

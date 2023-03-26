from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.matcher import Matcher
from nonebot.params import Arg, ArgPlainText, CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from LittlePaimon.database import Character
from LittlePaimon.utils import DRIVER, logger
from LittlePaimon.utils.alias import get_match_alias
from LittlePaimon.utils.genshin import GenshinInfoManager
from LittlePaimon.utils.message import CommandCharacter, CommandPlayer

from .classmodel import Dmg
from .database import CalcInfo, connect, disconnect
from .draw_character_detail import draw_chara_detail
from .role import get_role

DRIVER.on_startup(connect)
DRIVER.on_shutdown(disconnect)

__plugin_meta__ = PluginMetadata(
    name="纳西妲计算",
    description="纳西妲计算",
    usage="纳西妲计算",
    extra={
        "author": "pika",
        "priority": 20,
    },
)

NICKNAME = "纳西妲"

update = on_command(
    "upd",
    aliases={"nhd更新"},
    priority=9,
    block=True,
    state={
        "pm_name": "upd",
        "pm_description": '更新你的原神玩家和角色数据，绑定cookie后数据更详细，加上"天赋"可以更新天赋等级',
        "pm_usage": "upd<角色名>",
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
        logger.info("Nahida面板", "➤", {"用户": user_id, "UID": uid})
        for character in characters:
            character_info = await gim.get_character(name=character, data_source="enka")
            if character_info:
                await CalcInfo.update(user_id, uid, character_info)
                logger.success("Nahida面板", f"{character_info.name}更新成功")
                msg = f"{character_info.name}已更新"
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
    await CalcInfo.filter(user_id=user_id, uid=uid).delete()
    await clear.finish("已成功清除", at_sender=True)


nhd = on_command(
    "nhd",
    priority=10,
    block=True,
    state={
        "pm_name": "nhd",
        "pm_description": "查看指定角色的详细面板数据及伤害计算",
        "pm_usage": "nhd<角色名>",
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
            logger.info("Nahida面板", "➤", {"用户": user_id, "UID": uid})
            for character in characters:
                character_info = await gim.get_character(
                    name=character, data_source="enka"
                )
                if not character_info:
                    logger.info("Nahida面板", "➤➤", {"角色": character}, "没有该角色信息", False)
                    msg = f"\n暂无你{character}信息，请在游戏内展柜放置该角色"
                else:
                    data = await CalcInfo.filter(
                        user_id=user_id, uid=uid, name=character_info.name
                    ).first()
                    if data is None:
                        await CalcInfo.update(user_id, uid, character_info)
                        data = await CalcInfo.filter(
                            user_id=user_id, uid=uid, name=character_info.name
                        ).first()
                    img = await draw_chara_detail(uid, character_info, data)
                    logger.info("Nahida面板", "➤➤➤", {}, "制图完成", True)
                    msg += img
        else:
            # 当查询对象有多个时，只查询第一个角色
            for player in players:
                gim = GenshinInfoManager(player.user_id, player.uid)
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


set_info = on_command(
    "set",
    priority=10,
    block=True,
    state={
        "pm_name": "set_info",
        "pm_description": "查看指定角色的详细面板数据及伤害计算",
        "pm_usage": "set<角色名>",
        "pm_priority": 4,
    },
)


@set_info.handle()
async def _(
    event: MessageEvent,
    state: T_State,
    players=CommandPlayer(only_cn=False),
    characters=CommandCharacter(),
):
    logger.info("Nahida设置", "开始执行")
    user_id, uid = players[0].user_id, players[0].uid
    try:
        gim = GenshinInfoManager(user_id, uid)
        character_info = await gim.get_character(name=characters[0], data_source="enka")
        if character_info:
            calc_info = await CalcInfo.get_or_none(
                user_id=user_id, uid=uid, name=character_info.name
            )
            if calc_info is None:
                await set_info.finish("请先在虚空中录入角色", at_sender=True)
            else:
                state["chara"], state["calc"] = character_info, calc_info
                state["state"], state["msg"] = "0", Message("0")
                state["uid"] = uid
    except KeyError as e:
        await set_info.finish(
            f"获取角色信息失败，缺少{e}的数据，可能是Enka.Network接口出现问题", at_sender=True
        )
    except Exception as e:
        await set_info.finish(f"获取角色信息失败，错误信息：{e}", at_sender=True)


@set_info.got("msg")
async def _(
    event: MessageEvent,
    bot: Bot,
    state: T_State,
    feedback: str = ArgPlainText("msg"),
):
    """条件状态机"""
    state_num: str = state["state"]
    calc_info: CalcInfo = state["calc"]
    convers = "请选择需要设置的内容：\n0：取消\n1：增益\n2：伤害权重\n3：队友\n4：流派\n5：共鸣\n6：保存更改"
    match state_num:
        case "0":
            state["state"] = "1"
            await set_info.reject(convers, at_sender=True)
        case "1":
            match feedback:
                case "0":
                    await set_info.finish(f"好吧，有需要再找{NICKNAME}", at_sender=True)
                case "1":
                    msg = []
                    for i, buff in enumerate(calc_info.buffs):
                        content = f"{i+1}:{buff.name}\n{buff.setting.dsc}\n状态:{buff.setting.state}"
                        msg.append(
                            {
                                "type": "node",
                                "data": {
                                    "name": NICKNAME,
                                    "uin": event.self_id,
                                    "content": content,
                                },
                            }
                        )
                    msg.append(
                        {
                            "type": "node",
                            "data": {
                                "name": NICKNAME,
                                "uin": event.self_id,
                                "content": "更改格式：<序号>-<标记>，多项更改用空格分割\n例：0-4 1-5",
                            },
                        }
                    )
                    state["buffs"] = calc_info.buffs
                    if isinstance(event, GroupMessageEvent):
                        await bot.call_api(
                            "send_group_forward_msg",
                            group_id=event.group_id,
                            messages=msg,
                        )
                    elif isinstance(event, PrivateMessageEvent):
                        await bot.call_api(
                            "send_private_forward_msg",
                            user_id=event.user_id,
                            messages=msg,
                        )
                    state["state"] = "1-1"
                    await set_info.reject()
                case "2":
                    msg = []
                    for i, dmg in enumerate(calc_info.dmgs):
                        content = (
                            f"{i}:{dmg.name}\n{dmg.dsc}\n权重:{dmg.weight}\n"
                            + f"去除增益:{','.join(dmg.exclude_buff)}"
                        )
                        msg.append(
                            {
                                "type": "node",
                                "data": {
                                    "name": NICKNAME,
                                    "uin": event.self_id,
                                    "content": content,
                                },
                            }
                        )
                    msg.append(
                        {
                            "type": "node",
                            "data": {
                                "name": NICKNAME,
                                "uin": event.self_id,
                                "content": "请选择需要调整的序号",
                            },
                        }
                    )
                    if isinstance(event, GroupMessageEvent):
                        await bot.call_api(
                            "send_group_forward_msg",
                            group_id=event.group_id,
                            messages=msg,
                        )
                    elif isinstance(event, PrivateMessageEvent):
                        await bot.call_api(
                            "send_private_forward_msg",
                            user_id=event.user_id,
                            messages=msg,
                        )
                    state["state"] = "1-2"
                    state["dmgs"] = calc_info.dmgs
                    state["dmg"] = calc_info.dmgs[i]
                    await set_info.reject()
                case "3":
                    state["state"] = "1-3"
                    await set_info.reject("请指定队友")
                case "4":
                    role = get_role(name=calc_info.name)
                    msg = ""
                    for i, cate in enumerate(role.cate_list):
                        msg += f"{i+1}：{cate}\n"
                    state["ctgs"] = role.cate_list
                    state["state"] = "1-4"
                    await set_info.reject(msg)
                case "5":
                    msg = "输入最多两种元素"
                    state["state"] = "1-5"
                    await set_info.reject(msg)
                case "6":
                    await calc_info.save()
                    await CalcInfo.update(event.user_id, state["uid"], state["chara"])
                    await set_info.finish("已保存设置")
                case _:
                    await set_info.send("请正确选择序号")
                    await set_info.reject(convers)
        # 增益
        case "1-1":
            for pair in feedback.split():
                idx, label = pair.split("-")
                if idx.isdigit() and (idx := int(idx)) < len(calc_info.buffs):
                    setting = calc_info.buffs[idx - 1].setting
                    if label in ["-", "○"]:
                        if label == 0:
                            setting.label = "-"
                        else:
                            setting.label = "○"
                    else:
                        setting.label = label
            state["state"] = "1"
            await set_info.reject(convers)
        # 伤害
        case "1-2":
            msg = "1：设置权重\n2：设置不生效的增益（提供序号）"
            state["state"] = "1-2-x"
            await set_info.reject(msg)
        case "1-2-x":
            match feedback:
                case "1":
                    msg = "请输入权重"
                    state["state"] = "1-2-1"
                    await set_info.reject(msg)
                case "2":
                    msg = "请输入不需要生效的增益序号"
                    state["state"] = "1-2-2"
                    await set_info.reject(msg)
                case _:
                    await set_info.reject("请正确选择序号")
        case "1-2-1":
            if feedback.isdigit() or feedback == "-1":
                dmg: Dmg = state["dmg"]
                dmg.weight = min(int(feedback), 10)
                state["state"] = "1"
                await set_info.reject(convers)
        case "1-2-2":
            for idx in feedback.split():
                dmgs: list[Dmg] = state["dmgs"]
                if idx.isdigit() and (idx := int(idx)) <= len(dmgs):
                    dmg: Dmg = state["dmg"]
                    dmg.exclude_buff.append(dmgs[idx].name)
                    state["state"] = "1"
                    await set_info.reject(convers)
        # 队友
        case "1-3":
            for name in feedback.split():
                partn: dict
                if partn := get_match_alias(name):
                    calc_info.partner.append(partn.get("角色")[0])
            state["state"] = "1"
            await set_info.reject(convers)
        # 流派
        case "1-4":
            if feedback.isdigit():
                num = int(feedback)
                if num < len(state["ctgs"]):
                    calc_info.category = state["ctgs"][num - 1]
            state["state"] = "1"
            await set_info.reject(convers)
        # 共鸣
        case "1-5":
            calc_info.resonance = ""
            for char in feedback:
                if char in ["火", "雷", "水", "草", "风", "岩", "冰"]:
                    calc_info.resonance += char
            state["state"] = "1"
            await set_info.reject(convers)

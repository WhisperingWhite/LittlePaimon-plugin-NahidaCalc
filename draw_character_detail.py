from LittlePaimon.database import Character
from LittlePaimon.utils.alias import get_chara_icon
from LittlePaimon.utils.genshin import GenshinTools
from LittlePaimon.utils.image import PMImage, font_manager as fm, load_image
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import ENKA_RES, RESOURCE_BASE_PATH
from .classmodel import BuffInfo, Dmg
from .Nahidatools import get_rank, check_effective
from .database import Data

element_type = ["物理", "火元素", "雷元素", "水元素", "草元素", "风元素", "岩元素", "冰元素"]
TALENT_ICON = RESOURCE_BASE_PATH / "talent"
CON_ICON = RESOURCE_BASE_PATH / "constellation"
WEAPON_ICON = RESOURCE_BASE_PATH / "weapon"
ARTIFACT_ICON = RESOURCE_BASE_PATH / "artifact"
ICON = RESOURCE_BASE_PATH / "icon"


async def draw_chara_detail(
    uid: str,
    info: Character,
    data: Data,
):
    img = PMImage(await load_image(ENKA_RES / f"背景_{info.element}.png"))

    buff_img = await draw_buff_pic(data.buffs)
    if buff_img:
        await img.stretch((730, 1377), buff_img.height + 667, "height")
        await img.paste(buff_img, (42, 1820))

    dmg_img = await draw_dmg_pic(data.dmgs)
    if dmg_img:
        await img.stretch((730, 1377), dmg_img.height + 667, "height")
        await img.paste(dmg_img, (42, 1820))

    # 立绘
    chara_img = await load_image(
        RESOURCE_BASE_PATH
        / "splash"
        / f'{get_chara_icon(chara_id=info.character_id, icon_type="splash")}.png'
    )
    if chara_img.height >= 630:
        chara_img = chara_img.resize((chara_img.width * 630 // chara_img.height, 630))
    else:
        chara_img = chara_img.resize(
            (chara_img.width, chara_img.height * 630 // chara_img.height)
        )
    await img.paste(chara_img, (770 - chara_img.width // 2, 20))
    await img.paste(await load_image(ENKA_RES / "底遮罩.png"), (0, 0))
    # 地区
    if info.name not in ["荧", "空", "埃洛伊"]:
        await img.paste(
            await load_image(ENKA_RES / f"{info.region}.png", size=(108, 108)), (25, 25)
        )

    await img.text(f"UID{uid}", 160, 100, fm.get("number.ttf", 48))
    await img.text(info.name, 45, 150, fm.get("优设标题黑.ttf", 72))
    name_length = img.text_length(info.name, fm.get("优设标题黑.ttf", 72))

    level_mask = await load_image(ENKA_RES / "等级遮罩.png")
    await img.paste(level_mask, (45 + name_length + 25, 172))
    await img.text(
        f"LV{info.level}",
        (40 + name_length + 25, 40 + name_length + 25 + 171),
        (172, 172 + 52),
        fm.get("number.ttf", 48),
        "#0e2944",
        "center",
    )
    # 属性值
    await img.text("生命值", 59, 267, fm.get("hywh.ttf", 34))
    await img.text(
        f"{info.prop.base_health}",
        450
        - img.text_length(f"+{info.prop.extra_health}", fm.get("number.ttf", 34))
        - 5,
        269,
        fm.get("number.ttf", 34),
        align="right",
    )
    await img.text(
        f"+{info.prop.extra_health}",
        450,
        269,
        fm.get("number.ttf", 34),
        "#59c538",
        "right",
    )

    await img.text("攻击力", 59, 324, fm.get("hywh.ttf", 34))
    await img.text(
        f"{info.prop.base_attack}",
        450
        - img.text_length(f"+{info.prop.extra_attack}", fm.get("number.ttf", 34))
        - 5,
        326,
        fm.get("number.ttf", 34),
        align="right",
    )
    await img.text(
        f"+{info.prop.extra_attack}",
        450,
        326,
        fm.get("number.ttf", 34),
        "#59c538",
        "right",
    )

    await img.text("防御力", 59, 382, fm.get("hywh.ttf", 34))
    await img.text(
        f"{info.prop.base_defense}",
        450
        - img.text_length(f"+{info.prop.extra_defense}", fm.get("number.ttf", 34))
        - 5,
        384,
        fm.get("number.ttf", 34),
        align="right",
    )
    await img.text(
        f"+{info.prop.extra_defense}",
        450,
        384,
        fm.get("number.ttf", 34),
        "#59c538",
        "right",
    )

    await img.text("暴击率", 59, 441, fm.get("hywh.ttf", 34))
    await img.text(
        f"{round(info.prop.crit_rate * 100, 1)}%",
        450,
        443,
        fm.get("number.ttf", 34),
        align="right",
    )

    await img.text("暴击伤害", 59, 498, fm.get("hywh.ttf", 34))
    await img.text(
        f"{round(info.prop.crit_damage * 100, 1)}%",
        450,
        500,
        fm.get("number.ttf", 34),
        align="right",
    )

    await img.text("元素精通", 59, 556, fm.get("hywh.ttf", 34))
    await img.text(
        str(int(info.prop.elemental_mastery)),
        450,
        558,
        fm.get("number.ttf", 34),
        align="right",
    )

    await img.text("元素充能效率", 59, 615, fm.get("hywh.ttf", 34))
    await img.text(
        f"{round(info.prop.elemental_efficiency * 100, 1)}%",
        450,
        617,
        fm.get("number.ttf", 34),
        align="right",
    )

    max_element = "物理", 0
    for e, v in info.prop.dmg_bonus.items():
        if v >= max_element[1]:
            max_element = e, v
    if max_element[1] == 0:
        max_element = info.element, 0
    await img.text(
        f"{max_element[0]}伤害加成"
        if max_element[0] == "物理"
        else f"{max_element[0]}元素伤害加成",
        59,
        674,
        fm.get("hywh.ttf", 34),
    )
    await img.text(
        f"{round(max_element[1] * 100, 1)}%",
        450,
        676,
        fm.get("number.ttf", 34),
        align="right",
    )

    # 天赋
    base_icon = await load_image(ENKA_RES / f"图标_{info.element}.png", mode="RGBA")
    base_icon_grey = await load_image(ENKA_RES / "图标_灰.png", mode="RGBA")
    if info.name in ["神里绫华", "莫娜"]:
        info.talents.pop(2)
    for i in range(3):
        await img.paste(base_icon.resize((132, 142)), (551 + i * 176, 633))
        await img.text(
            str(info.talents[i].level),
            (517 + 176 * i, 559 + 176 * i),
            690,
            fm.get("number.ttf", 34),
            "#0e2944",
            "center",
        )
        await img.paste(
            await load_image(
                TALENT_ICON / f"{info.talents[i].icon}.png", size=(57, 57), mode="RGBA"
            ),
            (588 + i * 176, 679),
        )

    # 命座
    lock = await load_image(ENKA_RES / "锁.png", mode="RGBA", size=(45, 45))
    t = 0
    for con in info.constellation:
        await img.paste(base_icon.resize((83, 90)), (510 + t * 84, 805))
        con_icon = await load_image(
            TALENT_ICON / f"{con.icon}.png", size=(45, 45), mode="RGBA"
        )
        await img.paste(con_icon, (529 + t * 84, 828))
        t += 1
    for t2 in range(t, 6):
        await img.paste(base_icon_grey.resize((83, 90)), (510 + t2 * 84, 805))
        await img.paste(lock, (530 + t2 * 84, 828))

    # 武器
    weapon_bg = await load_image(
        ICON / f"star{info.weapon.rarity}.png", size=(150, 150)
    )
    await img.paste(weapon_bg, (59, 757))
    weapon_icon = await load_image(
        WEAPON_ICON / f"{info.weapon.icon}.png", size=(150, 150), mode="RGBA"
    )
    await img.paste(weapon_icon, (59, 757))
    await img.text(info.weapon.name, 254, 759, fm.get("hywh.ttf", 34))

    star = await load_image(ENKA_RES / "star.png")
    for i in range(info.weapon.rarity):
        await img.paste(star, (254 + i * 30, 798))
    await img.text(
        f"LV{info.weapon.level}",
        (254, 254 + 98),
        (834, 864),
        fm.get("number.ttf", 27),
        "#0e2944",
        "center",
    )
    await img.text(f"精炼{info.weapon.affix_level}阶", 254, 879, fm.get("hywh.ttf", 34))

    # 圣遗物
    w = 380
    h = 937
    for artifact in info.artifacts:
        artifact_bg = await load_image(
            ICON / f"star{artifact.rarity}.png", size=(93, 93)
        )
        await img.paste(artifact_bg, (216 + w, 70 + h))
        a_icon = await load_image(
            ARTIFACT_ICON / f"{artifact.icon}.png", size=(93, 93), mode="RGBA"
        )
        await img.paste(a_icon, (217 + w, 70 + h))
        await img.text(artifact.name, 22 + w, 24 + h, fm.get("hywh.ttf", 36))
        rank = get_rank(data.scores.get_score(artifact.part))
        await img.text(
            f"{rank}-{data.scores.get_score(artifact.part):.2f}",
            22 + w,
            66 + h,
            fm.get("number.ttf", 28),
            "#ffde6b",
        )
        await img.paste(level_mask.resize((98, 30)), (21 + w, 97 + h))
        await img.text(
            f"+{artifact.level}",
            (21 + w, 21 + w + 98),
            99 + h,
            fm.get("number.ttf", 27),
            "black",
            "center",
        )
        await img.text(
            artifact.main_property.name, 21 + w, 134 + h, fm.get("hywh.ttf", 25)
        )
        value_text = (
            f"+{artifact.main_property.value}%"
            if artifact.main_property.name not in ["生命值", "攻击力", "元素精通"]
            else f"+{int(artifact.main_property.value)}"
        )
        await img.text(value_text, 21 + w, 168 + h, font=fm.get("number.ttf", 48))
        for j in range(len(artifact.prop_list)):
            if "百分比" in artifact.prop_list[j].name:
                text = artifact.prop_list[j].name.replace("百分比", "")
            else:
                text = artifact.prop_list[j].name
            await img.text(
                text,
                21 + w,
                230 + h + 50 * j,
                color="gold"
                if check_effective(
                    artifact.prop_list[j].name, data.valid_prop
                )
                else "#afafaf",
                font=fm.get("hywh.ttf", 25),
            )
            if artifact.prop_list[j].name not in ["攻击力", "防御力", "生命值", "元素精通"]:
                num = "+" + str(artifact.prop_list[j].value) + "%"
            else:
                num = "+" + str(int(artifact.prop_list[j].value))
            await img.text(
                num,
                307 + w,
                230 + h + 50 * j,
                color="gold"
                if check_effective(
                    artifact.prop_list[j].name, data.valid_prop
                )
                else "#afafaf",
                font=fm.get("number.ttf", 25),
                align="right",
            )
        if info.artifacts.index(artifact) == 1:
            w = 42
            h += 437
        else:
            w += 338

    # 圣遗物评分
    total_rank = get_rank(data.scores.total_score / len(info.artifacts))
    rank_icon = await load_image(ENKA_RES / f"评分{total_rank[0]}.png", mode="RGBA")
    if len(total_rank) == 3:
        await img.paste(rank_icon, (65, 964))
        await img.paste(rank_icon, (115, 964))
        await img.paste(rank_icon, (165, 964))
        await img.text(
            f"{data.scores.total_score:.1f}", 220, 974, font=fm.get("number.ttf", 60)
        )
    elif len(total_rank) == 2:
        await img.paste(rank_icon, (95, 964))
        await img.paste(rank_icon, (145, 964))
        await img.text(
            f"{data.scores.total_score:.1f}", 205, 974, font=fm.get("number.ttf", 60)
        )
    else:
        await img.paste(rank_icon, (113, 964))
        await img.text(
            f"{data.scores.total_score:.1f}", 187, 974, font=fm.get("number.ttf", 60)
        )

    # 圣遗物套装
    suit = GenshinTools.get_artifact_suit(info.artifacts)
    if not suit:
        await img.text("未激活套装", 154, 1168, font=fm.get("hywh.ttf", 36))
    elif len(suit) == 1:
        artifact1 = await load_image(
            ARTIFACT_ICON / f"{suit[0][1]}.png", size=(110, 110), mode="RGBA"
        )
        await img.paste(artifact1, (46, 1130))
        await img.text(f"{suit[0][0][:2]}二件套", 154, 1168, font=fm.get("hywh.ttf", 36))
        await img.text("未激活套装", 154, 1292, font=fm.get("hywh.ttf", 36))
    else:
        if suit[0][0] == suit[1][0]:
            artifact1 = await load_image(
                ARTIFACT_ICON / f"{suit[0][1]}.png", size=(110, 110), mode="RGBA"
            )
            artifact2 = None
            await img.text(
                f"{suit[0][0][:2]}四件套", 154, 1168, font=fm.get("hywh.ttf", 36)
            )
            # await img.text(f'{suit[0][0][:2]}四件套', 154, 1292, font=fm.get('hywh.ttf', 36))
        else:
            artifact1 = await load_image(
                ARTIFACT_ICON / f"{suit[0][1]}.png", size=(110, 110), mode="RGBA"
            )
            artifact2 = await load_image(
                ARTIFACT_ICON / f"{suit[1][1]}.png", size=(110, 110), mode="RGBA"
            )
            await img.text(
                f"{suit[0][0][:2]}两件套", 154, 1168, font=fm.get("hywh.ttf", 36)
            )
            await img.text(
                f"{suit[1][0][:2]}两件套", 154, 1292, font=fm.get("hywh.ttf", 36)
            )
        await img.paste(artifact1, (46, 1130))
        await img.paste(artifact2, (46, 1255))

    await img.text(data.category, (22, 402), 1292, font=fm.get("hywh.ttf", 36))

    # 立绘
    await img.text(
        f'更新于{info.update_time.strftime("%m-%d %H:%M")}',
        (0, 1080),
        (img.height - 123, img.height - 80),
        fm.get("优设标题黑.ttf", 33),
        "#afafaf",
        "center",
    )
    await img.text(
        "Created by LittlePaimon | Powered by Enka.Network",
        (0, 1080),
        (img.height - 80, img.height - 40),
        fm.get("优设标题黑.ttf", 33),
        "white",
        "center",
    )

    return MessageBuild.Image(img, quality=75, mode="RGB")


async def draw_dmg_pic(dmg_list: list[Dmg]) -> PMImage:
    """
    绘制伤害图片
    :param dmg: 伤害字典
    :return: 伤害图片
    """
    height = 60 * len(dmg_list) - 20
    img = PMImage(size=(1002, height + 80), color=(0, 0, 0, 0), mode="RGBA")
    await img.draw_rounded_rectangle(
        (0, 0, img.width, img.height), 10, (14, 41, 68, 115)
    )
    await img.draw_line((250, 0), (250, 1002), (255, 255, 255, 75), 2)
    await img.draw_line((626, 60), (626, 120), (255, 255, 255, 75), 2)
    await img.draw_line((0, 60), (1002, 60), (255, 255, 255, 75), 2)
    await img.text(
        dmg_list[0].name, (0, 250), (0, 60), fm.get("hywh.ttf", 30), "white", "center"
    )
    await img.text(
        f"{dmg_list[0].weight:d}",
        (250, 1002),
        (0, 60),
        fm.get("number.ttf", 30),
        "white",
        "center",
    )
    await img.text(
        "伤害计算", (0, 250), (60, 120), fm.get("hywh.ttf", 30), "white", "center"
    )
    await img.text(
        "期望伤害", (250, 626), (60, 120), fm.get("hywh.ttf", 30), "white", "center"
    )
    await img.text(
        "暴击伤害", (626, 1002), (60, 120), fm.get("hywh.ttf", 30), "white", "center"
    )
    i = 2
    for dmg in dmg_list[1:]:
        if dmg.weight != 0:
            await img.draw_line((0, 60 * i), (1002, 60 * i), (255, 255, 255, 75), 2)
            await img.text(
                dmg.dsc,
                (0, 250),
                (60 * i, 60 * (i + 1)),
                fm.get("hywh.ttf", 30),
                "white",
                "center",
            )
            await img.draw_line(
                (626, 60 * i), (626, 60 * (i + 1)), (255, 255, 255, 75), 2
            )
            await img.text(
                f"{dmg.exp_value:.0f}",
                (250, 626),
                (60 * i, 60 * (i + 1)),
                fm.get("number.ttf", 30),
                "white",
                "center",
            )
            await img.text(
                f"{dmg.crit_value:.0f}",
                (626, 1002),
                (60 * i, 60 * (i + 1)),
                fm.get("number.ttf", 30),
                "white",
                "center",
            )
            i += 1

    await img.crop((0, 0, 1002, 60 * i))
    return img


async def draw_buff_pic(buff_list: list[BuffInfo]) -> PMImage:
    """
    绘制增益图片
    :param buff: 增益列表
    :return: 增益图片
    """
    height = 60 * len(buff_list) - 20
    img = PMImage(size=(1002, height + 80), color=(0, 0, 0, 0), mode="RGBA")
    await img.draw_rounded_rectangle(
        (0, 0, img.width, img.height), 10, (14, 41, 68, 115)
    )
    # await img.draw_line((250, 0), (250, 1002), (255, 255, 255, 75), 2)
    # await img.draw_line((626, 0), (626, 60), (255, 255, 255, 75), 2)
    await img.draw_line((0, 60), (1002, 60), (255, 255, 255, 75), 2)
    await img.text("增益列表", (0, 250), (0, 60), fm.get("hywh.ttf", 30), "white", "center")
    i = 1
    for buff in buff_list:
        if buff.setting.state != "×":
            await img.draw_line((0, 60 * i), (1002, 60 * i), (255, 255, 255, 75), 2)
            await img.text(
                buff.source,
                (0, 250),
                (60 * i, 60 * (i + 1)),
                fm.get("hywh.ttf", 30),
                "white",
                "center",
            )
            await img.draw_line(
                (250, 60 * i), (250, 60 * (i + 1)), (255, 255, 255, 75), 2
            )
            await img.text(
                buff.buff.dsc,
                (250, 1002),
                (60 * i, 60 * (i + 1)),
                fm.get("hywh.ttf", 30),
                "white",
                "center",
            )
            i += 1
    await img.crop((0, 0, 1002, 60 * i))
    return img

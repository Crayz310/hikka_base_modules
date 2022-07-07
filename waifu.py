# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/color/480/000000/hinata.png
# scope: inline
# scope: hikka_only
# meta developer: @hikarimods

import asyncio
import functools
import logging

import requests
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)
categories = ["waifu", "neko", "shinobu", "megumin", "cuddle", "cry", "hug", "awoo", "kiss", "lick", "pat", "smug", "bonk", "yeet", "blush", "smile", "wave", "highfive", "handhold", "nom", "bite", "glomp", "slap"]  # fmt: skip
nsfw_categories = ["waifu", "neko", "trap", "blowjob"]  # fmt: skip


async def photo(type_: str, category: str) -> list:
    if category in nsfw_categories and category not in categories:
        type_ = "nsfw"

    ans = (
        await utils.run_sync(
            requests.post,
            f"https://api.waifu.pics/many/{type_}/{category}",
            json={"exclude": []},
        )
    ).json()

    if "files" not in ans:
        logger.error(ans)
        return []

    return ans["files"]


@loader.tds
class WaifuMod(loader.Module):
    """Unleash best waifus of all time"""

    strings = {"name": "Waifu"}

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:waifu")
        )

    async def stats_task(self):
        await asyncio.sleep(60)
        await self._client.inline_query(
            "@hikkamods_bot",
            f"#statload:{','.join(list(set(self.allmodules._hikari_stats)))}",
        )
        delattr(self.allmodules, "_hikari_stats")
        delattr(self.allmodules, "_hikari_stats_task")

    async def client_ready(self, client, db):
        self._db = db
        self._client = client

        if not hasattr(self.allmodules, "_hikari_stats"):
            self.allmodules._hikari_stats = []

        self.allmodules._hikari_stats += ["waifu"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def waifucmd(self, message: Message):
        """[nsfw] [category] - Send waifu"""
        category = (
            [
                category
                for category in categories + nsfw_categories
                if category in utils.get_args_raw(message)
            ]
            or [
                categories[0]
                if "nsfw" not in utils.get_args_raw(message)
                else nsfw_categories[0]
            ]
        )[0]

        await self.inline.gallery(
            message=message,
            next_handler=functools.partial(
                photo,
                type_=("nsfw" if "nsfw" in utils.get_args_raw(message) else "sfw"),
                category=category,
            ),
            caption=f"<b>{('🔞 NSFW' if 'nsfw' in utils.get_args_raw(message) else '👨‍👩‍👧 SFW')}</b>: <i>{category}</i>",
            preload=10,
        )

    async def waifuscmd(self, message: Message):
        """Show available categories"""
        await utils.answer(
            message,
            "\n".join(
                [
                    " | ".join(i)
                    for i in utils.chunks([f"<code>{i}</code>" for i in categories], 5)
                ]
            )
            + "\n<b>NSFW:</b>\n"
            + "\n".join(
                [
                    " | ".join(i)
                    for i in utils.chunks(
                        [f"<code>{i}</code>" for i in nsfw_categories], 5
                    )
                ]
            ),
        )

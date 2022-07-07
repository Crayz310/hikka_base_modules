#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://i.imgur.com/C5dbpMA.jpeg
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.1.7
# requires: grapheme
# meta developer: @hikarimods

import asyncio
import logging

import grapheme
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)


def trashguy(text):
    DISTANCE = 5
    SPACER = "\u0020\u2800"
    text = list(grapheme.graphemes(text))
    return [
        utils.escape_html(i)
        for i in utils.array_sum(
            [
                [
                    f"🗑{SPACER * i}(> ^_^)>{SPACER * (DISTANCE - i)}{''.join(text[offset:])}"
                    for i in range(DISTANCE)
                ]
                + [
                    f"🗑{SPACER * (DISTANCE - i)}{current_symbol}<(^_^ <){SPACER * i}{''.join(text[offset + 1:])}"
                    for i in range(DISTANCE)
                ]
                for offset, current_symbol in enumerate(text)
            ]
        )
    ]


@loader.tds
class TrashGuyMod(loader.Module):
    """Sadly, not powered by libtguy (http://zac.cy/trashguy), google, facebook or anything else"""

    strings = {
        "name": "TrashGuy",
        "done": "🗑 \\ (•◡•) / 🗑\n\u0020\u2800\u0020\u2800<b>Done!</b>\u0020\u2800\u0020\u2800",
    }

    strings_ru = {
        "done": "🗑 \\ (•◡•) / 🗑\n\u0020\u2800\u0020\u2800<b>Я закончил!</b>\u0020\u2800\u0020\u2800",
    }

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:trashguy")
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

        self.allmodules._hikari_stats += ["trashguy"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def tguyicmd(self, message: Message):
        """<text> - TrashGuy Inline"""
        await self.animate(
            message,
            trashguy(utils.get_args_raw(message) or "hikari's brain")
            + [self.strings("done")],
            interval=1,
            inline=True,
        )

    async def tguycmd(self, message: Message):
        """<text> - TrashGuy"""
        await self.animate(
            message,
            trashguy(utils.get_args_raw(message) or "hikari's brain")
            + [self.strings("done")],
            interval=1,
        )

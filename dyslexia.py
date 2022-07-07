# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/240/000000/apple-music-lyrics.png
# meta developer: @hikarimods
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.1.7

import asyncio
import re
from random import shuffle

from telethon.tl.types import Message

from .. import loader, utils


def dyslex(text: str) -> str:
    res = ""
    for word in text.split():
        newline = False
        if "\n" in word:
            word = word.replace("\n", "")
            newline = True

        to_shuffle = re.sub(r"[^a-zA-Zа-яА-Я0-9]", "", word)[1:-1]
        shuffled = list(to_shuffle)
        shuffle(shuffled)

        res += word.replace(to_shuffle, "".join(shuffled)) + " "
        if newline:
            res += "\n"

    return res


@loader.tds
class DyslexiaMod(loader.Module):
    """Shows the text as how you would see it if you have dyslexia"""

    strings = {"name": "Dyslexia", "no_text": "🎈 <b>You need to provide text</b>"}

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:dislexia")
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

        self.allmodules._hikari_stats += ["dislexia"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def dyslexcmd(self, message: Message):
        """<text | reply> - Show, how people with dyslexia would have seen this text"""
        args = utils.get_args_raw(message)
        if not args:
            try:
                args = (await message.get_reply_message()).text
            except Exception:
                return await utils.answer(message, self.strings("no_text"))

        await self.animate(
            message,
            [dyslex(args) for _ in range(20)],
            interval=2,
            inline=True,
        )

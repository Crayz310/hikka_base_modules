# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/color-glass/344/phone.png
# requires: requests
# scope: hikka_only
# meta developer: @hikarimods

import asyncio
import logging

import requests
from telethon.tl.types import Message
from telethon.utils import get_display_name

from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class BulkCheckMod(loader.Module):
    """Check all members of chat for leaked numbers"""

    strings = {
        "name": "BulkCheck",
        "processing": "🌊 <b>Processing...</b>",
        "no_pm": "🚫 <b>This command can be used only in chat</b>",
        "leaked": "🌊 <b>Leaked numbers in current chat:</b>\n\n{}",
        "404": "😔 <b>No leaked numbers found here</b>",
    }

    strings_ru = {
        "processing": "🌊 <b>Работаю...</b>",
        "no_pm": "🚫 <b>Эту команду нужно выполнять в чате</b>",
        "leaked": "🌊 <b>Слитые номера в этом чате:</b>\n\n{}",
        "404": "😔 <b>Тут нет слитых номеров</b>",
    }

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:bulkcheck")
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

        self.allmodules._hikari_stats += ["bulkcheck"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def bcheckcmd(self, message: Message):
        """Bulk check using Murix database"""
        if message.is_private:
            await utils.answer(message, self.strings("no_pm"))
            return

        message = await utils.answer(message, self.strings("processing"))

        results = []
        async for member in self._client.iter_participants(message.peer_id):
            result = (
                await utils.run_sync(
                    requests.get,
                    f"http://api.murix.ru/eye?uid={member.id}&v=1.2",
                )
            ).json()
            if result["data"] != "NOT_FOUND":
                results += [
                    f"<b>▫️ <a href=\"tg://user?id={member.id}\">{utils.escape_html(get_display_name(member))}</a></b>: <code>+{result['data']}</code>"
                ]

        await utils.answer(
            message,
            self.strings("leaked").format("\n".join(results))
            if results
            else self.strings("404"),
        )

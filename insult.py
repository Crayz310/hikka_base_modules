#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/color/480/000000/angry--v1.png
# meta developer: @hikarimods

import asyncio
import random

from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class PoliteInsultMod(loader.Module):
    """If you need to insult but to be intelligent"""

    strings = {"name": "PoliteInsult"}

    async def on_unload(self):
        asyncio.ensure_future(
            self._client.inline_query("@hikkamods_bot", "#statunload:insult")
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

        self.allmodules._hikari_stats += ["insult"]

        if not hasattr(self.allmodules, "_hikari_stats_task"):
            self.allmodules._hikari_stats_task = asyncio.ensure_future(
                self.stats_task()
            )

    async def insultocmd(self, message: Message):
        """Use when angry"""
        adjectives_start = [
            "вспыльчивый(-ая)",
            "невоспитанный(-ая)",
            "осточертевший(-ая) мне",
            "глуповатый(-ая)",
            "надменный(-ая)",
            "неиндивидуалистичный(-ая)",
            "неиндифферентный(-ая)",
            "недисциплинированный(-ая)",
        ]
        nouns = ["человек", "участник(-ца) данного чата"]
        starts = [
            "Не хочу делать поспешных выводов, но",
            "Я, конечно, не могу утверждать, и это мое субъективное мнение, но",
            "Проанализировав ситуацию, я могу высказать свое субъективное мнение. Оно заключается в том, что",
            "Не пытаясь никого осокорбить, а лишь высказывая свою скромную точку зрения, которая не влияет на точку зрения других людей, могу сказать, что",
            "Не преследуя попытку затронуть какие-либо социальные меньшинства, хочу сказать, что",
        ]
        ends = ["!!!!", "!", "."]
        start = random.choice(starts)
        adjective_start = random.choice(adjectives_start)
        adjective_mid = random.choice(adjectives_start)
        noun = random.choice(nouns)
        end = random.choice(ends)
        insult = (
            (
                f"{start} ты - {adjective_start} {adjective_mid}"
                + (" " if adjective_mid else "")
            )
            + noun
        ) + end

        await utils.answer(message, insult)

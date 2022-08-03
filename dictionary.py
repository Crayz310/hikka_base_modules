#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.hikari.gay/dictionary_icon.png
# meta banner: https://mods.hikariatama.ru/badges/dictionary.jpg
# meta developer: @hikarimods
# requires: aiohttp urllib bs4
# scope: inline
# scope: hikka_only
# scope: hikka_min 1.2.10

import logging
import re
from urllib.parse import quote_plus

import aiohttp
from bs4 import BeautifulSoup
from telethon.tl.types import Message

from .. import loader, utils

logging.getLogger("charset_normalizer").setLevel(logging.ERROR)

headers = {
    "accept": "text/html",
    "user-agent": "Hikka userbot",
}


@loader.tds
class UrbanDictionaryMod(loader.Module):
    """Search for words meaning in urban dictionary"""

    strings = {
        "name": "UrbanDictionary",
        "no_args": "🚫 <b>Specify term to find the definition for</b>",
        "err": "🧞‍♂️ <b>I don't know about term </b><code>{}</code>",
        "no_page": "🚫 Can't switch to that page",
        "meaning": "🧞‍♂️ <b><u>{}</u></b>:\n\n<i>{}</i>",
    }

    strings_ru = {
        "no_args": "🚫 <b>Укажи, для какого слова искать определение</b>",
        "err": "🧞‍♂️ <b>Я не знаю, что значит </b><code>{}</code>",
        "no_page": "🚫 Нельзя переключиться на эту страницу",
        "meaning": "🧞‍♂️ <b><u>{}</u></b>:\n\n<i>{}</i>",
        "_cmd_doc_mean": "<слова> - Найти определение слова в UrbanDictionary",
        "_cls_doc": "Ищет определения слов в UrbanDictionary",
    }

    async def scrape(self, term: str) -> str:
        term = "".join(
            [
                i.lower()
                for i in term
                if i.lower()
                in "абвгдежзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz "
            ]
        )
        endpoint = "https://www.urbandictionary.com/define.php?term={}"
        url = endpoint.format(quote_plus(term.lower()))
        async with aiohttp.ClientSession() as session:
            async with session.request("GET", url, headers=headers) as resp:
                html = await resp.text()

        soup = BeautifulSoup(re.sub(r"<br.*?>", "♠️", html), "html.parser")

        return [
            definition.get_text().replace("♠️", "\n")
            for definition in soup.find_all("div", class_="meaning")
        ]

    async def meancmd(self, message: Message):
        """<term> - Find definition of the word in urban dictionary"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        means = await self.scrape(args)

        if not means:
            await utils.answer(message, self.strings("err").format(args))
            return

        await self.inline.list(
            message=message,
            strings=[self.strings("meaning").format(args, mean) for mean in means],
        )

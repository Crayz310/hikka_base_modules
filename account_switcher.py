__version__ = (2, 0, 1)

# █ █ ▀ █▄▀ ▄▀█ █▀█ ▀    ▄▀█ ▀█▀ ▄▀█ █▀▄▀█ ▄▀█
# █▀█ █ █ █ █▀█ █▀▄ █ ▄  █▀█  █  █▀█ █ ▀ █ █▀█
#
#              © Copyright 2022
#
#          https://t.me/hikariatama
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://img.icons8.com/fluency/240/000000/guest-male.png
# meta developer: @hikarimods
# scope: hikka_only
# scope: hikka_min 1.1.15

import io
import logging
import re
from typing import Union

from aiogram.types import Message as AiogramMessage
from aiogram.utils.exceptions import ChatNotFound
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import Message as TelethonMessage

from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)


@loader.tds
class AccountSwitcherMod(loader.Module):
    """Allows you to easily switch between different profiles"""

    strings = {
        "name": "AccountSwitcher",
        "account_saved": '📼 <b><a href="https://t.me/c/{}/{}">Account</a> saved!</b>',
        "restore_btn": "👆 Restore",
        "desc": "This chat will handle your saved profiles",
        "first_name_restored": "✅ First name restored\n",
        "first_name_unsaved": "🔘 First name not saved\n",
        "last_name_restored": "✅ First name restored\n",
        "last_name_unsaved": "🔘 First name not saved\n",
        "bio_restored": "✅ Bio restored\n",
        "bio_unsaved": "🔘 Bio not saved\n",
        "data_not_restored": "🚫 First name not restored\n🚫 Last name not restored\n🚫 Bio not restored\n",
        "pfp_restored": "✅ Profile photo restored",
        "pfp_unsaved": "🔘 Profile photo not saved",
    }

    strings_ru = {
        "account_saved": '📼 <b><a href="https://t.me/c/{}/{}">Аккаунт</a> сохранен!</b>',
        "restore_btn": "👆 Восстановить",
        "desc": "Тут будут появляться сохраненные профили",
        "first_name_restored": "✅ Имя восстановлено\n",
        "first_name_unsaved": "🔘 Имя не сохранялось\n",
        "last_name_restored": "✅ Фамилия восстановлена\n",
        "last_name_unsaved": "🔘 Фамилия не сохранялась\n",
        "bio_restored": "✅ Био восстановлено\n",
        "bio_unsaved": "🔘 Био не сохранялось\n",
        "data_not_restored": "🚫 Имя не восстановлено\n🚫 Фамилия не восстановлена\n🚫 Био не восстановлено\n",
        "pfp_restored": "✅ Аватарка восстановлена",
        "pfp_unsaved": "🔘 Аватарка не сохранялась",
        "_cmd_doc_accsave": "Сохранить аккаунт для последующего использования",
        "_cls_doc": "Позволяет быстро переключаться между разными аккаунтами",
    }

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self._accs_db, is_new = await utils.asset_channel(
            self._client,
            "hikka-acc-switcher",
            self.strings("desc"),
            silent=True,
            archive=True,
            avatar="https://raw.githubusercontent.com/hikariatama/assets/master/hikka-acc-switcher.png",
            _folder="hikka",
        )

        self._accs_db_id = int(f"-100{self._accs_db.id}")

        if not is_new:
            return

        try:
            await self._client(
                InviteToChannelRequest(self._accs_db, [self.inline.bot_username])
            )
        except Exception:
            logger.warning("Unable to invite logger to chat. Maybe he's already there?")

    async def _save_acc(
        self,
        photo: Union[bytes, None],
        first_name: str,
        last_name: str,
        bio: str,
        no_retry: bool = False,
    ) -> int:
        info = (
            f"<code>{utils.escape_html(first_name)}</code> "
            f"<code>{utils.escape_html(last_name)}</code>\n\n"
            f"<b>Bio</b>: <code>{utils.escape_html(bio)}</code>\n"
        )

        try:
            if photo is not None:
                photo_io = io.BytesIO(photo)
                photo_io.name = "pfp.jpg"

                return (
                    await self.inline.bot.send_document(
                        self._accs_db_id,
                        photo_io,
                        caption=info,
                        parse_mode="HTML",
                        reply_markup=self.inline.generate_markup(
                            {"text": self.strings("restore_btn"), "data": "accrest"}
                        ),
                    )
                ).message_id
            else:
                return (
                    await self.inline.bot.send_message(
                        self._accs_db_id,
                        info,
                        parse_mode="HTML",
                        reply_markup=self.inline.generate_markup(
                            {"text": self.strings("restore_btn"), "data": "accrest"}
                        ),
                    )
                ).message_id
        except ChatNotFound:
            if no_retry:
                logger.exception("Can't restore account")
                return

            await self._client(
                InviteToChannelRequest(self._accs_db, [self.inline.bot_username])
            )

            return await self._save_acc(
                photo,
                first_name,
                last_name,
                bio,
                no_retry=True,
            )

    async def accrest_callback_handler(self, call: InlineCall):
        if call.data != "accrest":
            return

        await call.answer(await self._restore(call.message), show_alert=True)

    async def accsavecmd(self, message: TelethonMessage):
        """Save account for future restoring"""
        full = await self._client(GetFullUserRequest("me"))
        acc = await self._client.force_get_entity("me")

        message_id = await self._save_acc(
            (await self._client.download_profile_photo(acc, bytes))
            if full.full_user.profile_photo
            else None,
            getattr(acc, "first_name", "None"),
            getattr(acc, "last_name", "None"),
            (
                getattr(full.full_user, "about", "None")
            ),
        )

        await utils.answer(
            message, self.strings("account_saved").format(self._accs_db.id, message_id)
        )

    async def _restore(self, reply: Union[TelethonMessage, AiogramMessage]) -> str:
        log = ""

        first_name, last_name, bio = list(
            map(
                lambda x: x.replace("&gt;", ">")
                .replace("&lt;", "<")
                .replace("&quot;", '"')
                .replace("&amp;", "&"),
                re.findall(
                    r"<code>(.*?)</code>",
                    getattr(reply, "html_text", reply.text),
                    flags=re.S,
                ),
            )
        )

        if first_name == "None":
            first_name = None

        if last_name == "None":
            last_name = None

        if bio == "None":
            bio = None

        try:
            await self._client(UpdateProfileRequest(first_name, last_name, bio))

            log += (
                self.strings("first_name_restored")
                if first_name
                else self.strings("first_name_unsaved")
            )

            log += (
                self.strings("last_name_restored")
                if last_name
                else self.strings("last_name_unsaved")
            )

            log += (
                self.strings("bio_restored")
                if bio
                else self.strings("bio_unsaved")
            )
        except Exception:
            logger.exception("Can't restore account due to")
            log += self.strings("data_not_restored")

        try:
            upload = await self._client.upload_file(
                await self._client.download_file(reply.media, bytes)
            )
            await self._client(UploadProfilePhotoRequest(upload))
            log += self.strings("pfp_restored")
        except Exception:
            try:
                file = io.BytesIO()
                await reply.document.download(destination_file=file)

                await self._client(
                    UploadProfilePhotoRequest(
                        await self._client.upload_file(file),
                    )
                )

                log += self.strings("pfp_restored")
            except Exception:
                log += self.strings("pfp_unsaved")

        return re.sub(r"\n{2,}", "\n", log)

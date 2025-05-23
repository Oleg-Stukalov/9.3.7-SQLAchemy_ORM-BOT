from asyncio import sleep

from aiogram import Router
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.requests import (
    add_score, get_total_score_for_user, delete_user_data_from_db
)
from cachetools import TTLCache

router = Router(name="commands router")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Доступные команды:\n"
                        "/play - играть,\n"
                         "/stats - получить сумму очков по всем играм,\n"
                         "/last3 - вывести 3 последние игры,\n"
                         "/deleteme - удалить данные о себе из БД."
    )


@router.message(Command("play"))
async def cmd_warn(
    message: Message,
    session: AsyncSession,
):
    dice_msg = await message.answer_dice(
        emoji=DiceEmoji.DICE
    )
    score = dice_msg.dice.value
    await add_score(session, message.from_user.id, score)
    await sleep(5.0)  # примерное время анимации кубика на клиенте
    await message.answer(f"Выпало число {score}")


@router.message(Command("stats"))
async def cmd_stats(
    message: Message,
    session: AsyncSession,
):
    total_score: int = await get_total_score_for_user(
        session, message.from_user.id
    )
    await message.answer(
        f"Привет, {message.from_user.first_name}! "
        f"Твой суммарный счёт: {total_score}"
    )


@router.message(Command("deleteme"))
async def cmd_stats(
    message: Message,
    session: AsyncSession,
    **data: dict,  # capture extra data passed from middleware
):
    user_id = message.from_user.id
    await delete_user_data_from_db(session, user_id)
    # Safely access the user_cache
    user_cache: TTLCache = data.get("user_cache")
    if user_cache:
        user_cache.pop(user_id, None)
    await message.answer(f"Ваши данные удалены из БД.")
import structlog
from aiogram import F, Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup
from fluent.runtime import FluentLocalization
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()
logger = structlog.get_logger()


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    l10n: FluentLocalization,
):
    await message.answer(
        l10n.format_value("cmd-start"),
        parse_mode=None,
    )


@router.message(Command("donate_1"))
@router.message(Command("donate_25"))
@router.message(Command("donate_50"))
@router.message(Command("donate"))
async def cmd_donate(
    message: Message,
    command: CommandObject,
    l10n: FluentLocalization,
):
    # Если это команда /donate ЧИСЛО,
    # тогда вытаскиваем число из текста команды
    if command.command != "donate":
        amount = int(command.command.split("_")[1])
    # В противном случае пытаемся парсить пользовательский ввод
    else:
        # Проверка на число и на его диапазон
        if (
            command.args is None
            or not command.args.isdigit()
            or not 1 <= int(command.args) <= 2500
        ):
            await message.answer(
                l10n.format_value("custom-donate-input-error")
            )
            return
        amount = int(command.args)

    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Оплатить {amount} XTR",
        pay=True
    )
    builder.button(
        text="Отменить покупку",
        callback_data="cancel"
    )
    builder.adjust(1)


    # Для платежей в Telegram Stars список цен
    # ОБЯЗАН состоять РОВНО из 1 элемента
    prices = [LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(
        title=l10n.format_value("invoice-title"),
        description=l10n.format_value(
            "invoice-description",
            {"starsCount": amount}
        ),
        prices=prices,
        # provider_token Должен быть пустым
        provider_token="",
        # В пейлоайд можно передать что угодно,
        # например, айди того, что именно покупается
        payload=f"{amount}_stars",
        # XTR - это код валюты Telegram Stars
        currency="XTR",
        reply_markup=builder.as_markup()
    )


@router.message(Command("paysupport"))
async def cmd_paysupport(
    message: Message,
    l10n: FluentLocalization
):
    await message.answer(l10n.format_value("cmd-paysupport"))


@router.message(Command("refund"))
async def cmd_refund(
    message: Message,
    bot: Bot,
    command: CommandObject,
    l10n: FluentLocalization,
):
    transaction_id = command.args
    if transaction_id is None:
        await message.answer(
            l10n.format_value("refund-no-code-provided")
        )
        return
    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id
        )
        await message.answer(
            l10n.format_value("refund-successful")
        )
    except TelegramBadRequest as error:
        if "CHARGE_NOT_FOUND" in error.message:
            text = l10n.format_value("refund-code-not-found")
        elif "CHARGE_ALREADY_REFUNDED" in error.message:
            text = l10n.format_value("refund-already-refunded")
        else:
            # При всех остальных ошибках – такой же текст,
            # как и в первом случае
            text = l10n.format_value("refund-code-not-found")
        await message.answer(text)
        return


@router.message(Command("donate_link"))
async def cmd_link(
    message: Message,
    bot: Bot,
    l10n: FluentLocalization,
):
    invoice_link = await bot.create_invoice_link(
        title=l10n.format_value("invoice-title"),
        description=l10n.format_value(
            "invoice-description",
            {"starsCount": 1}
        ),
        prices=[LabeledPrice(label="XTR", amount=1)],
        provider_token="",
        payload="demo",
        currency="XTR"
    )
    await message.answer(
        l10n.format_value(
            "invoice-link-text",
            {"link": invoice_link}
        )
    )


@router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
    l10n: FluentLocalization,
):
    await pre_checkout_query.answer(ok=True)
    # await pre_checkout_query.answer(
    #     ok=False,
    #     error_message=l10n.format_value("pre-checkout-failed-reason")
    # )


@router.message(F.successful_payment)
async def on_successful_payment(
    message: Message,
    l10n: FluentLocalization,
):
    await logger.ainfo(
        "Получен новый донат!",
        amount=message.successful_payment.total_amount,
        from_user_id=message.from_user.id,
        user_username=message.from_user.username
    )
    await message.answer(
        l10n.format_value(
            "payment-successful",
            {"id": message.successful_payment.telegram_payment_charge_id}
        ),
        # Это эффект "огонь" из стандартных реакций
        message_effect_id="5104841245755180586",
    )

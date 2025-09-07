# Import necessary modules for bot operation
import asyncio                # For asynchronous programming
import logging                # For logging bot operations

# Import main aiogram components
from aiogram import Bot, Dispatcher                          # Core aiogram classes
from aiogram.client.default import DefaultBotProperties      # Bot default settings
from aiogram.enums import ParseMode                          # Text formatting modes

# Import configuration and handlers
from config_reader import config                             # Bot token and settings
from handlers import in_pm, bot_in_group, admin_changes_in_group, events_in_group


async def main():
    """
    Main function to run the bot
    Sets up logging, dispatcher, and starts polling
    """
    # Configure logging with detailed format
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Create dispatcher and bot instance
    dp = Dispatcher()
    bot = Bot(
        config.bot_token.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML  # Set HTML as default parse mode
        )
    )
    
    # Include all routers for different types of updates
    dp.include_routers(
        in_pm.router,                    # Private message handlers
        events_in_group.router,          # Group event handlers
        bot_in_group.router,             # Bot status in group handlers
        admin_changes_in_group.router    # Admin changes handlers
    )

    # Get list of chat administrators for permission checking
    admins = await bot.get_chat_administrators(config.main_chat_id)
    admin_ids = {admin.user.id for admin in admins}

    # Start polling for updates
    await dp.start_polling(bot, admins=admin_ids)


if __name__ == '__main__':
    # Run the bot when script is executed directly
    asyncio.run(main())
# Import necessary modules
import asyncio  # For working with asynchronous programming

# Import main aiogram components
from aiogram import Bot, Dispatcher  # Main classes for creating a bot

# Import configuration
from config_reader import config  # Loading settings from configuration file

# Import handlers from different modules
from handlers import questions, different_types


# Bot launch function
async def main():
    """Main function for setting up and running the bot"""
    
    # Create bot instance with token from configuration
    bot = Bot(token=config.bot_token.get_secret_value())
    
    # Create dispatcher for handling events
    dp = Dispatcher()

    # Register routers with handlers
    # The order matters - first registered router has higher priority
    dp.include_routers(questions.router, different_types.router)

    # Alternative way to register routers one per line
    # dp.include_router(questions.router)
    # dp.include_router(different_types.router)

    # Start bot and skip all accumulated updates.
    # Useful when restarting bot to avoid processing old messages.
    # And yes, this method can be used even if you have polling.
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start polling for updates from Telegram
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Run main function in asynchronous mode
    # Entry point to the program
    asyncio.run(main())

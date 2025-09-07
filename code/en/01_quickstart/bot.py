# Import necessary modules
import asyncio                  # For working with asynchronous programming
import logging                  # For logging bot operation
from datetime import datetime   # For working with date and time

# Import main aiogram components
from aiogram import Bot, Dispatcher, types      # Main classes for creating a bot
from aiogram.enums.dice_emoji import DiceEmoji  # Emojis for dice games
from aiogram.filters.command import Command     # Filter for handling commands

# Import configuration
from config_reader import config  # Loading settings from configuration file

# Configure logging to display information about bot operation
logging.basicConfig(level=logging.INFO)

# Create bot instance with token from configuration
bot = Bot(token=config.bot_token.get_secret_value())

# Create dispatcher for handling events
dp = Dispatcher()

# Save bot startup time in dispatcher context
# This value will be available in all handlers through dependency injection
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

# Handler for /start command
# Decorator automatically registers function as handler
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handler for /start command - greets the user"""
    await message.answer("Hello!")


# Handler for /test1 command
# Simple example of command handling using decorator
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
    """Handler for /test1 command - sends test message"""
    await message.reply("Test 1")


# Handler for /test2 command
# Without decorator, as it's registered manually in main() function
# This is an alternative way of registering handlers
async def cmd_test2(message: types.Message):
    """Handler for /test2 command - demonstrates manual registration"""
    await message.reply("Test 2")


@dp.message(Command("answer"))
async def cmd_answer(message: types.Message):
    """Demonstration of answer() method - sends regular response"""
    await message.answer("This is a simple answer")


@dp.message(Command("reply"))
async def cmd_reply(message: types.Message):
    """Demonstration of reply() method - sends response with quote"""
    await message.reply('This is a reply with a "reply"')


@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    """Sending game dice - demonstration of special message types"""
    await message.answer_dice(emoji=DiceEmoji.DICE)


@dp.message(Command("add_to_list"))
async def cmd_add_to_list(message: types.Message, mylist: list[int]):
    """
    Demonstration of dependency injection - getting list from dispatcher context
    mylist is passed automatically when bot starts
    """
    mylist.append(7)
    await message.answer("Number 7 added")


@dp.message(Command("show_list"))
async def cmd_show_list(message: types.Message, mylist: list[int]):
    """Shows current contents of list from context"""
    await message.answer(f"Your list: {mylist}")


@dp.message(Command("info"))
async def cmd_info(message: types.Message, started_at: str):
    """
    Demonstration of getting data from dispatcher context
    started_at is automatically passed from dp["started_at"]
    """
    await message.answer(f"Bot launched {started_at}")


async def main():
    """Main function for setting up and running the bot"""
    
    # Demonstration of manual handler registration
    # Alternative to using decorators
    dp.message.register(cmd_test2, Command("test2"))

    # Start bot and skip all accumulated updates.
    # Useful when restarting bot to avoid processing old messages.
    # And yes, this method can be used even if you have polling.
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start bot in long polling mode
    # mylist=[1, 2, 3] is passed to dispatcher context for dependency injection
    await dp.start_polling(bot, mylist=[1, 2, 3])


if __name__ == "__main__":
    # Run main function in asynchronous mode
    # Entry point to the program
    asyncio.run(main())
# Import necessary modules for working with messages and media
import asyncio                 # For asynchronous programming
import logging                 # For logging bot operations
import re                      # For regular expressions in deep link processing
from datetime import datetime  # For working with time in messages

# Import main aiogram components
from aiogram import Bot, Dispatcher, html, F                                                         # Core aiogram classes and utilities
from aiogram.client.default import DefaultBotProperties                                              # Bot default settings
from aiogram.enums import ParseMode                                                                  # Text formatting modes (HTML, Markdown)
from aiogram.filters import Command, CommandObject, CommandStart                                     # Command filters
from aiogram.types import Message, FSInputFile, URLInputFile, BufferedInputFile, LinkPreviewOptions  # Message and file types
from aiogram.utils.formatting import as_list, as_marked_section, Bold, as_key_value, HashTag         # Text formatting utilities
from aiogram.utils.markdown import hide_link                                                         # Hidden link utility
from aiogram.utils.media_group import MediaGroupBuilder                                              # For creating albums

# Import configuration
from config_reader import config  # Bot token and settings

# Create bot instance with HTML parsing by default
# This means all messages will be parsed as HTML unless specified otherwise
bot = Bot(
    token=config.bot_token.get_secret_value(),
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML  # Set HTML as default parse mode
    )
)

# Create dispatcher for handling events
dp = Dispatcher()

# Configure logging to see bot operations in console
logging.basicConfig(level=logging.INFO)


@dp.message(Command("test"))
async def any_message(message: Message):
    """
    Handler for /test command - demonstrates different parse modes
    Shows how the same text is rendered with different formatting
    """
    # HTML formatting (bold text)
    await message.answer("Hello, <b>world</b>!", parse_mode=ParseMode.HTML)
    
    # Markdown V2 formatting (bold text with escaped exclamation mark)
    await message.answer("Hello, *world*\!", parse_mode=ParseMode.MARKDOWN_V2)
    
    # HTML formatting using bot's default parse mode (HTML)
    await message.answer("Message with <u>HTML markup</u>")
    
    # No formatting - parse_mode=None disables all markup
    await message.answer("Message without <s>any markup</s>", parse_mode=None)


@dp.message(Command("hello"))
async def cmd_hello(message: Message):
    """
    Handler for /hello command - demonstrates safe text formatting
    Uses html.quote() to escape special characters in user input
    """
    await message.answer(
        f"Hello, {html.bold(html.quote(message.from_user.full_name))}",
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("advanced_example"))
async def cmd_advanced_example(message: Message):
    """
    Handler for /advanced_example command - demonstrates advanced text formatting
    Uses aiogram's formatting utilities to create structured messages
    """
    # Create structured content using formatting utilities
    content = as_list(
        # Success section with checkmark markers
        as_marked_section(
            Bold("Success:"),
            "Test 1",
            "Test 3", 
            "Test 4",
            marker="✅ ",  # Green checkmark for successful tests
        ),
        # Failed section with X markers
        as_marked_section(
            Bold("Failed:"),
            "Test 2",
            marker="❌ ",  # Red X for failed tests
        ),
        # Summary section with key-value pairs
        as_marked_section(
            Bold("Summary:"),
            as_key_value("Total", 4),
            as_key_value("Success", 3),
            as_key_value("Failed", 1),
            marker="  ",  # Indent for summary items
        ),
        HashTag("#test"),  # Add hashtag for categorization
        sep="\n\n",  # Separate sections with double newlines
    )
    # Send the formatted content
    await message.answer(**content.as_kwargs())


@dp.message(Command("settimer"))
async def cmd_settimer(
        message: Message,
        command: CommandObject  # CommandObject contains command arguments
):
    """
    Handler for /settimer command - demonstrates command argument parsing
    Expected format: /settimer <time> <message>
    """
    # Check if any arguments were provided
    # If no arguments are passed, then command.args will be None
    if command.args is None:
        await message.answer(
            "Error: no arguments passed"
        )
        return
    
    # Try to split the arguments into two parts by the first encountered space
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    # If there are less than two parts, a ValueError will be thrown
    except ValueError:
        await message.answer(
            "Error: incorrect command format. Example:\n"
            "/settimer <time> <message>"
        )
        return
    
    # Confirm timer creation (in real bot, you'd start an actual timer)
    await message.answer(
        "Timer added!\n"
        f"Time: {delay_time}\n"
        f"Text: {text_to_send}"
    )


@dp.message(Command("gif"))
async def send_gif(message: Message):
    """
    Handler for /gif command - demonstrates sending animations/GIFs
    Shows caption positioning above media
    """
    await message.answer_animation(
        animation="<gif file_id>",     # Replace with actual file_id
        caption="Me today:",
        show_caption_above_media=True  # Show caption above the GIF
    )


# Custom command prefix examples
@dp.message(Command("custom1", prefix="%"))
async def cmd_custom1(message: Message):
    """
    Handler for %custom1 command - demonstrates custom command prefix
    Uses % instead of the default / prefix
    """
    await message.answer("I see the command!")


@dp.message(Command("custom2", prefix="/!"))
async def cmd_custom2(message: Message):
    """
    Handler for /custom2 or !custom2 commands
    Multiple prefixes can be specified as a string
    """
    await message.answer("I see this one too!")


# Deep link handlers - multiple ways to handle /start with parameters
@dp.message(Command("help"))
@dp.message(CommandStart(
    deep_link=True, magic=F.args == "help"  # Matches /start help
))
async def cmd_start_help(message: Message):
    """
    Handler for /help command or /start help deep link
    Demonstrates multiple decorators on one handler
    """
    await message.answer("This is the help message")


@dp.message(CommandStart(
    deep_link=True,
    magic=F.args.regexp(re.compile(r'book_(\d+)'))  # Matches /start book_123
))
async def cmd_start_book(
        message: Message,
        command: CommandObject
):
    """
    Handler for /start book_<number> deep links
    Uses regex to extract book number from deep link parameter
    """
    book_number = command.args.split("_")[1]  # Extract number after "book_"
    await message.answer(f"Sending book №{book_number}")


@dp.message(Command("links"))
async def cmd_links(message: Message):
    """
    Handler for /links command - demonstrates link preview customization
    Shows different ways to control how links are displayed
    """
    # Two links that will be included in the final message
    links_text = (
        "https://nplus1.ru/news/2024/05/23/voyager-1-science-data"
        "\n"
        "https://t.me/telegram"
    )
    
    # Example 1: Disable link previews completely
    options_1 = LinkPreviewOptions(is_disabled=True)
    await message.answer(
        f"No link previews\n{links_text}",
        link_preview_options=options_1
    )

    # -------------------- #

    # Example 2: Small preview
    # To use prefer_small_media, you must also specify the url
    options_2 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True  # Show compact preview
    )
    await message.answer(
        f"Small preview\n{links_text}",
        link_preview_options=options_2
    )

    # -------------------- #

    # Example 3: Large preview
    # To use prefer_large_media, you must also specify the url
    options_3 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_large_media=True  # Show expanded preview
    )
    await message.answer(
        f"Large preview\n{links_text}",
        link_preview_options=options_3
    )

    # -------------------- #

    # Example 4: Combine settings - small preview above text
    options_4 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True,
        show_above_text=True  # Position preview above message text
    )
    await message.answer(
        f"Small preview above text\n{links_text}",
        link_preview_options=options_4
    )

    # -------------------- #

    # Example 5: Choose which link to preview (not necessarily the first one)
    options_5 = LinkPreviewOptions(
        url="https://t.me/telegram"  # Preview second link instead of first
    )
    await message.answer(
        f"Preview of the non-first link\n{links_text}",
        link_preview_options=options_5
    )


@dp.message(Command("hidden_link"))
async def cmd_hidden_link(message: Message):
    """
    Handler for /hidden_link command - demonstrates invisible link embedding
    Uses hide_link() to embed an image invisibly in the message
    """
    await message.answer(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Telegram Documentation: *exists*\n"
        f"Users: *do not read documentation*\n"
        f"Groosha:"
    )


@dp.message(Command('images'))
async def upload_photo(message: Message):
    """
    Handler for /images command - demonstrates different ways to send images
    Shows various InputFile types for sending photos to Telegram
    """
    # Here we will store the file_id of sent files to use them later
    file_ids = []

    # Method 1: BufferedInputFile - for sending files from memory/bytes
    # To demonstrate BufferedInputFile, we use the "classic"
    # file opening through `open()`. But generally speaking,
    # this method is best suited for sending bytes from RAM
    # after performing some manipulations, for example, editing through Pillow
    with open("buffer_emulation.jpg", "rb") as image_from_buffer:
        result = await message.answer_photo(
            BufferedInputFile(
                image_from_buffer.read(),
                filename="image from buffer.jpg"
            ),
            caption="Image from buffer"
        )
        file_ids.append(result.photo[-1].file_id)

    # Method 2: FSInputFile - for sending files directly from file system
    # This is the most common method for local files
    image_from_pc = FSInputFile("image_from_pc.jpg")
    result = await message.answer_photo(
        image_from_pc,
        caption="Image from file on computer"
    )
    file_ids.append(result.photo[-1].file_id)

    # Method 3: URLInputFile - for sending files from URLs
    # Telegram will download the file from the URL
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    result = await message.answer_photo(
        image_from_url,
        caption="Image via URL"
    )
    file_ids.append(result.photo[-1].file_id)
    
    # Show all collected file_ids for future reference
    await message.answer("Sent files:\n"+"\n".join(file_ids))


@dp.message(Command("album"))
async def cmd_album(message: Message):
    """
    Handler for /album command - demonstrates sending media groups (albums)
    Shows how to use MediaGroupBuilder for creating photo/video albums
    """
    # Create a media group builder with a general caption
    # The caption will be shown under the entire album
    album_builder = MediaGroupBuilder(
        caption="General caption for the future album"
    )
    
    # Method 1: Generic add() method - specify type explicitly
    album_builder.add(
        type="photo",
        media=FSInputFile("image_from_pc.jpg")
        # caption="Caption for specific media"  # Individual captions are optional
    )
    
    # Method 2: Type-specific methods - if we know the type right away
    # instead of the general add() we can immediately call add_<type>
    album_builder.add_photo(
        # For links or file_id just specify the value directly
        media="https://picsum.photos/seed/groosha/400/300"
    )
    
    # Method 3: Using existing file_id (most efficient for repeated use)
    album_builder.add_photo(
        media="<your file_id>"  # Replace with actual file_id from previous uploads
    )
    
    # Send the media group - don't forget to call build()!
    await message.answer_media_group(
        media=album_builder.build()
    )


@dp.message(F.text)
async def extract_data(message: Message):
    """
    Handler for any text message - demonstrates entity extraction
    Extracts URLs, emails, and code snippets from message entities
    Shows proper way to extract text from entities
    """
    # Initialize data dictionary with default values
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "code": "<N/A>"
    }
    
    # Get entities from the message (can be None if no entities)
    entities = message.entities or []
    
    # Process each entity found in the message
    for item in entities:
        if item.type in data.keys():
            # WRONG way (can cause issues with Unicode):
            # data[item.type] = message.text[item.offset : item.offset+item.length]
            
            # CORRECT way - use extract_from() method:
            # This method properly handles Unicode characters and encoding
            data[item.type] = item.extract_from(message.text)
    
    # Send the extracted data back to user
    # Use html.quote() to safely display potentially dangerous content
    await message.reply(
        "Here's what I found:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Code: {html.quote(data['code'])}"
    )

@dp.message(F.text)
async def echo_with_time(message: Message):
    """
    Alternative text handler - demonstrates message echoing with timestamp
    NOTE: This handler is currently overridden by the extract_data handler above
    To use this handler, comment out the previous @dp.message(F.text) handler
    """
    # Get current time in the PC's timezone
    time_now = datetime.now().strftime('%H:%M')
    
    # Create underlined text using html.underline() utility
    added_text = html.underline(f"Created at {time_now}")
    
    # Send new message with original HTML text + timestamp
    # message.html_text preserves original formatting
    await message.answer(f"{message.html_text}\n\n{added_text}")


@dp.message(F.animation)
async def echo_gif(message: Message):
    """
    Handler for GIF/animation messages - demonstrates animation echoing
    Responds with the same animation using its file_id
    """
    await message.reply_animation(message.animation.file_id)


@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    """
    Handler for photo messages - demonstrates file downloading
    Downloads the highest quality photo to local storage
    """
    # message.photo[-1] gets the highest quality version of the photo
    # Photos are stored as array with different resolutions
    await bot.download(
        message.photo[-1],
        destination=f"/tmp/{message.photo[-1].file_id}.jpg"
    )


@dp.message(F.sticker)
async def download_sticker(message: Message, bot: Bot):
    """
    Handler for sticker messages - demonstrates sticker downloading
    Downloads sticker in WebP format to local storage
    """
    await bot.download(
        message.sticker,
        destination=f"/tmp/{message.sticker.file_id}.webp"
    )


@dp.message(F.new_chat_members)
async def somebody_added(message: Message):
    """
    Handler for new chat members - demonstrates group chat events
    Triggered when someone joins the group/supergroup
    """
    # Process each new member (can be multiple in one event)
    for user in message.new_chat_members:
        await message.reply(f"Hello, {user.full_name}")


async def main():
    """
    Main function to run the bot
    Sets up polling and handles cleanup
    """
    # Start bot and skip all accumulated updates.
    # Useful when restarting bot to avoid processing old messages.
    # And yes, this method can be used even if you have polling.
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start bot in long polling mode
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Run main function in asynchronous mode
    # Entry point to the program
    asyncio.run(main())

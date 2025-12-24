import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from loguru import logger

import config
from src.database import db_manager
from src.bot import commands, handlers, queries, admin, advanced_search

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=config.LOG_LEVEL
)
logger.add(
    "logs/bot_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    level=config.LOG_LEVEL
)

async def main():
    """Main function để chạy bot"""
    
    logger.info("=" * 50)
    logger.info("Starting Telegram Accounting Bot")
    logger.info("=" * 50)
    
    # Initialize database
    try:
        logger.info("Initializing database...")
        db_manager.create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)
    
    # Initialize bot
    try:
        bot = Bot(token=config.TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
        
        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"Bot initialized: @{bot_info.username}")
        
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        sys.exit(1)
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(commands.router)
    dp.include_router(handlers.router)
    dp.include_router(queries.router)
    dp.include_router(admin.router)
    dp.include_router(advanced_search.router)
    
    logger.info("All routers registered")
    
    # Start polling
    try:
        logger.info("Bot is now running. Press Ctrl+C to stop.")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error during polling: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot shut down successfully")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated")

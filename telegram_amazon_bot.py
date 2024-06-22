import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

TAG, URL = range(2)

# Function to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Hello! Please send me your Amazon affiliate tag ID.')
    return TAG

# Function to handle tag input
async def handle_tag(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['tag'] = update.message.text.strip()
    await update.message.reply_text('Got it! Now, please send me the Amazon URL.')
    return URL

# Function to handle URL input
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tag_id = context.user_data.get('tag')
    amazon_url = update.message.text.strip()

    if not tag_id:
        await update.message.reply_text('Tag ID is missing. Please start again by sending /start.')
        return ConversationHandler.END

    try:
        # Parse the Amazon URL
        parsed_url = urlparse(amazon_url)
        query_params = parse_qs(parsed_url.query)
        query_params['tag'] = tag_id

        # Rebuild the URL with the tag parameter
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse(parsed_url._replace(query=new_query))

        # Respond with the new Amazon URL
        await update.message.reply_text(f'Amazon Affiliate URL: {new_url}')
    except Exception as e:
        logger.error(f'Error handling URL: {e}')
        await update.message.reply_text('There was an error processing your request.')

    return ConversationHandler.END

# Function to cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

# Main function to run the bot
def main() -> None:
    # Replace 'YOUR_TOKEN' with the token you got from BotFather
    application = Application.builder().token('7235243073:AAFfV-_5nzsIgb31fmDce3y84tR_s9DGNLY').build()

    # Conversation handler for handling tag and URL
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TAG: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tag)],
            URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()

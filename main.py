import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler
)
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from scorebat import (
    prepare_api_links,
    prepare_youtube_videos,
    find_games_per_team,
    find_teams_per_country
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

COUNTRY, TEAM = range(2)
COUNTRIES = [
    'SPAIN',
    'GERMANY',
    'ENGLAND'
]

ENV = os.environ.get('ENV', 'stg')
PORT = int(os.environ.get('PORT', '8443'))
TOKEN = os.environ.get('TOKEN', '')

def start(update: Update, _: CallbackContext) -> int:
    logger.info(f"started for {update.message.from_user['username']}")

    keyboard = []
    for country in COUNTRIES:
        keyboard.append(InlineKeyboardButton(country, callback_data=country))
    reply_markup = InlineKeyboardMarkup([keyboard])

    update.message.reply_text('Country?', reply_markup=reply_markup)
    return COUNTRY


def country_selected(update: Update, context: CallbackContext) -> int:
    logger.info(f"country selected: {update.callback_query.data}")

    query = update.callback_query
    query.answer()

    games, teams = find_teams_per_country(query.data)
    context.user_data['games'] = games
    
    keyboard = []
    for team in teams:
        keyboard.append(InlineKeyboardButton(team, callback_data=team))
    reply_markup = InlineKeyboardMarkup.from_column(keyboard)

    query.edit_message_text('Team?', reply_markup=reply_markup)
    return TEAM


def team_selected(update: Update, context: CallbackContext) -> int:
    logger.info(f"team selected: {update.callback_query.data}")

    query = update.callback_query
    query.answer()

    games = find_games_per_team(context.user_data['games'], query.data)
    apis = prepare_api_links(games)
    videos = prepare_youtube_videos(apis)
    
    for video in videos:
        query.edit_message_text(video)

    return ConversationHandler.END


def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Use /start to test this bot.')


def main():
    updater = Updater(TOKEN)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            COUNTRY: [CallbackQueryHandler(country_selected)],
            TEAM: [CallbackQueryHandler(team_selected)],
        },
        fallbacks=[MessageHandler(Filters.text, help_command)],
    )

    updater.dispatcher.add_handler(conv_handler)

    if ENV == 'stg':
        logger.info('Starting polling')
        updater.start_polling()
    else:
        logger.info(f"Starting webhook on PORT {PORT}")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
        updater.bot.setWebhook(f"https://voetbot.herokuapp.com/{TOKEN}")

    updater.idle()


if __name__ == '__main__':
    main()

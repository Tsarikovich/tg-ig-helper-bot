import os

import telebot
from src import config, helping_functions, ig_bot_settings
from src.helping_functions import get_account_names
from src.InstagramHandler import InstagramHandler
from telebot import types


CURRENT_ACCOUNT = None
bot = telebot.TeleBot(os.environ['TOKEN'], parse_mode=None)


def auth(func):
    def wrapper(message):
        if message.from_user.id == config.ID_TELEGRAM_CHAT:
            func(message)

    return wrapper


@bot.message_handler(commands=['choose_account'])
@auth
def post(message):
    markup = types.InlineKeyboardMarkup()

    for account_name in get_account_names():
        markup.add(
            types.InlineKeyboardButton(
                account_name, callback_data=account_name
            )
        )

    bot.send_message(
        message.chat.id, text='Choose account:', reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data in get_account_names())
def callback_inline(call):
    global CURRENT_ACCOUNT

    CURRENT_ACCOUNT = call.data
    bot.send_message(
        config.ID_TELEGRAM_CHAT, text=f'Handling {CURRENT_ACCOUNT}'
    )


@bot.message_handler(commands=['current_account'])
@auth
def show_current_account(message):
    if CURRENT_ACCOUNT:
        bot.send_message(message.chat.id, text=CURRENT_ACCOUNT)
    else:
        bot.send_message(message.chat.id, text='No account is selected')


@bot.message_handler(
    regexp=r'/https?:\/\/w{0,3}\w*?\.(\w*?\.)'
    r'?\w{2,3}\S*|www\.(\w*?\.)?\w*?\.'
    r'\w{2,3}\S*|(\w*?\.)?\w*?\.\w{2,'
    r'3}[\/\?]\S*/ '
)
@auth
def process_url(message):
    url = message.text
    msg = bot.send_message(message.from_user.id, text='Enter caption:')
    bot.register_next_step_handler(msg, get_caption, url)


def get_caption(message, url):
    caption = message.text

    if caption != '-':
        caption = '\n'.join([caption, ig_bot_settings.CAPTION])
    else:
        caption = ig_bot_settings.CAPTION

    try:
        bot.send_message(message.from_user.id, 'Creating post...')
        ig_handler.process_url(CURRENT_ACCOUNT, url, caption)
        bot.send_message(message.from_user.id, 'Posted!')
    except Exception as e:
        bot.send_message(message.from_user.id, ' '.join(['Error:', str(e)]))


@bot.message_handler(commands=['generate_hashtags'])
@auth
def set_hashtags(message):
    msg = bot.send_message(
        message.from_user.id, text='Enter a few template hashtags:'
    )
    bot.register_next_step_handler(msg, get_hashtags)


def get_hashtags(message):
    helping_functions.generate_hashtags(message.text)
    bot.send_message(
        message.from_user.id,
        f'Generated new hashtags: \n{ig_bot_settings.HASHTAGS}',
    )


@bot.message_handler(commands=['templates'])
@auth
def show_templates(message):
    templates = 'Hashtags:\n' + ig_bot_settings.HASHTAGS
    templates = (
        templates + '\n' + 'Caption template:' + '\n' + ig_bot_settings.CAPTION
    )
    bot.send_message(message.from_user.id, text=templates)


@bot.message_handler(commands=['start_activity'])
@auth
def start_activity(message):
    bot.send_message(message.from_user.id, text="Oh, let's go...")
    ig_handler.public_activity()


if __name__ == '__main__':
    ig_handler = InstagramHandler(os.environ['accounts_list'])
    bot.polling()

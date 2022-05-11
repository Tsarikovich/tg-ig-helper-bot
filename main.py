import telebot
from telebot import types
import config
import helping_functions
from InstagramHandler import InstagramHandler
import os
import setConfig
from helping_functions import get_account_names

URL_TYPE_REGEXP = r"/https?:\/\/w{0,3}\w*?\.(\w*?\.)?\w{2,3}\S*|www\.(\w*?\.)?\w*?\.\w{2,3}\S*|(\w*?\.)?\w*?\.\w{2," \
                  r"3}[\/\?]\S*/ "

bot = telebot.TeleBot(os.environ['TOKEN'], parse_mode=None)
ig_handler = InstagramHandler(os.environ["accounts_list"])
URL, ACCOUNT_NAME = "", ""


@bot.message_handler(commands=['choose_account'])
def post(message):
    if message.from_user.id == config.ID_TELEGRAM_CHAT:
        markup = types.InlineKeyboardMarkup()

        for account_name in get_account_names():
            markup.add(types.InlineKeyboardButton(account_name, callback_data=account_name))

        bot.send_message(message.chat.id, text="Choose account:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in get_account_names())
def callback_inline(call):
    global ACCOUNT_NAME
    ACCOUNT_NAME = call.data
    bot.send_message(config.ID_TELEGRAM_CHAT, text=f"Handling {ACCOUNT_NAME}")


@bot.message_handler(commands=['current_account'])
def show_current_account(message):
    if message.from_user.id == config.ID_TELEGRAM_CHAT:
        if ACCOUNT_NAME != "":
            bot.send_message(message.chat.id, text=ACCOUNT_NAME)
        else:
            bot.send_message(message.chat.id, text="No account is selected")

@bot.message_handler(regexp=URL_TYPE_REGEXP)
def process_url(message):
    if message.from_user.id == config.ID_TELEGRAM_CHAT:
        global URL
        URL = message.text

        msg = bot.send_message(message.from_user.id, text="Enter caption:")
        bot.register_next_step_handler(msg, get_caption)


def get_caption(message):
    caption = message.text

    if caption != "-":
        caption = "\n".join([caption, config.CAPTION])
    else:
        caption = config.CAPTION

    try:
        bot.send_message(message.from_user.id, "Creating post...")
        ig_handler.process_url(ACCOUNT_NAME, URL, caption)
        bot.send_message(message.from_user.id, "Posted!")
    except Exception as e:
        bot.send_message(message.from_user.id, " ".join(["Error:", str(e)]))


@bot.message_handler(commands=['generate_hashtags'])
def set_hashtags(message):
    if message.from_user.id == config.ID_TELEGRAM_CHAT:
        msg = bot.send_message(message.from_user.id, text="Eter a few template hashtags:")
        bot.register_next_step_handler(msg, get_hashtags)


def get_hashtags(message):
    helping_functions.generate_hashtags(message.text)
    bot.send_message(message.from_user.id, f"Generated new hashtags: \n{config.HASHTAGS}")


@bot.message_handler(commands=['templates'])
def show_templates(message):
    if message.from_user.id == config.ID_TELEGRAM_CHAT:
        templates = "\n".join(["Hashtags:", config.HASHTAGS])
        templates = "\n".join([templates, "Caption template:", config.CAPTION])

        bot.send_message(message.from_user.id, text=templates)


@bot.message_handler(commands=['start_activity'])
def start_activity(message):
    if message.from_user.id == config.ID_TELEGRAM_CHAT:
        bot.send_message(message.from_user.id, text="Oh, let's go...")
        ig_handler.public_activity()

if __name__ == '__main__':
    bot.polling()
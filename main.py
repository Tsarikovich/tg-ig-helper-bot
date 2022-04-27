import telebot
import config
from api import InstagramHandler
import os

URL_TYPE_REGEXP = r"/https?:\/\/w{0,3}\w*?\.(\w*?\.)?\w{2,3}\S*|www\.(\w*?\.)?\w*?\.\w{2,3}\S*|(\w*?\.)?\w*?\.\w{2," \
                  r"3}[\/\?]\S*/ "

bot = telebot.TeleBot(os.environ.get('TOKEN', None), parse_mode=None)
ig_handler = InstagramHandler()
URL = ""


@bot.message_handler(regexp=URL_TYPE_REGEXP)
def post(message):
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
        ig_handler.process_url(URL, caption)
        bot.send_message(message.from_user.id, "Posted!")
    except Exception as e:
        bot.send_message(message.from_user.id, " ".join(["Error:", str(e)]))


@bot.message_handler(commands=['set_hashtags'])
def set_hashtags(message):
    if message.from_user.id == config.ID_TELEGRAM_CHAT:
        msg = bot.send_message(message.from_user.id, text="Enter hashtags:")
        bot.register_next_step_handler(msg, get_hashtags)


def get_hashtags(message):
    hashtags = message.text
    config.HASHTAGS = hashtags
    bot.send_message(message.from_user.id, "Hashtags have set successfully")


@bot.message_handler(commands=['templates'])
def show_templates(message):
    if message.from_user.id == config.ID_TELEGRAM_CHAT:
        templates = "\n".join(["Hashtags:", config.HASHTAGS])
        templates = "\n".join([templates, "Caption template:", config.CAPTION])

        bot.send_message(message.from_user.id, text=templates)


if __name__ == '__main__':
    bot.polling()

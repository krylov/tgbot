from argparse import ArgumentParser
from configparser import ConfigParser
from os import environ
from os.path import join
from telebot import TeleBot


BOT_CONFIGS_ENV = "TG_CONFIG_PATH"


def create_bot():
    path = environ.get(BOT_CONFIGS_ENV)
    if not path:
        raise Exception("The '{}' environment variable should "
                        "be declared.".format(BOT_CONFIGS_ENV))
    parser = ArgumentParser()
    parser.add_argument("-b", "--bot", help="The name of bot that will be run",
                        default='')
    args = parser.parse_args()
    if not args.bot:
        raise Exception("The bot name shouldn't be empty.")
    full_bot_path = join(path, args.bot) + ".ini"
    config = ConfigParser()
    try:
        config.read(full_bot_path)
        token = config.get('main', 'token')
    except Exception as exc:
        raise exc
    return TeleBot(token)

bot = create_bot()


@bot.message_handler(commands=['trn'])
def handle_start_help(message):
    pass


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    try:
        n = int(message.text)
        response = str(n*n)
    except:
        response = "This is not number"

    bot.send_message(message.chat.id, response)


if __name__ == '__main__':
    bot.polling(none_stop=True)

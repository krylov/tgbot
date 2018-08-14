from argparse import ArgumentParser
from configparser import ConfigParser
from importlib import import_module
from os import environ
from os.path import join
from requests.exceptions import ConnectionError, ReadTimeout
from telebot import TeleBot
from time import sleep


BOT_CONFIGS_ENV = "TG_CONFIG_PATH"


class CustomTeleBot:
    def __init__(self, token):
        self._bot = TeleBot(token)

        @self._bot.message_handler(commands=['trn'])
        def handle_start_help(message):
            pass

        @self._bot.message_handler(content_types=["text"])
        def make_response(message):
            self._bot.send_message(message.chat.id,
                                   handler.make_response(message))

    def run(self):
        self._bot.polling(none_stop=True)


def create_tools():
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
    msghandler = import_module('betpammhandler')

    return CustomTeleBot(token), msghandler.betpammhandler.BetPammHandler()


if __name__ == '__main__':
    while True:
        try:
            bot, handler = create_tools()
            bot.run()
            break
        except (ConnectionError, ReadTimeout) as exc:
            print("Error: {}".format(exc))
            sleep(10)

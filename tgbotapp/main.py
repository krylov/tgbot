from argparse import ArgumentParser
from configparser import ConfigParser
from importlib import import_module
import logging
import logging.config
from os.path import join
from requests.exceptions import ConnectionError, ReadTimeout
from telebot import TeleBot
from time import sleep


class CustomTeleBot:
    def __init__(self, token):
        self._bot = TeleBot(token)

        @self._bot.message_handler(commands=['start_send', 'stop_send'])
        def execute_command(message):
            handler.execute_command(self._bot, message)

        @self._bot.message_handler(content_types=['text'])
        def make_response(message):
            self._bot.send_message(message.chat.id,
                                   handler.make_response(message),
                                   parse_mode="html")

    def run(self):
        self._bot.polling(none_stop=True)


def create_tools():
    parser = ArgumentParser()
    parser.add_argument("-b", "--bot", required=True,
                        help="The name of bot that will be run")
    parser.add_argument("-d", "--config-dir-path", help="The config dir path")
    parser.add_argument("-l", "--logging-path", required=True,
                        help="The name of logging configuration file")
    args = parser.parse_args()
    logging.config.fileConfig(args.logging_path)
    full_bot_path = join(args.config_dir_path, args.bot) + ".ini"
    config = ConfigParser()
    try:
        config.read(full_bot_path)
        token = config.get("main", "token")
        handler_name = config.get('main', "handler")
        handler_settings = config.items("handler")
        handler_settings = dict(handler_settings)
    except Exception as exc:
        raise exc
    msghandler = import_module(handler_name)

    return (CustomTeleBot(token),
            msghandler.msghandler.MessageHandler(**handler_settings))


if __name__ == "__main__":

    while True:
        try:
            bot, handler = create_tools()
            bot.run()
            break
        except (ConnectionError, ReadTimeout) as exc:
            print("Error: {}".format(exc))
            sleep(10)

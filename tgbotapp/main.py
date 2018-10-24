from argparse import ArgumentParser
from configparser import ConfigParser
from importlib import import_module
import logging
import logging.config
from os.path import join
from requests.exceptions import ConnectionError, ReadTimeout
import signal
from telebot import TeleBot
from time import sleep


class CustomTeleBot:

    def __init__(self, token, handlers):
        self._bot = TeleBot(token)
        commands = []
        for handler in handlers:
            commands += handler.commands

        @self._bot.message_handler(commands=commands)
        def execute_command(message):
            log.info("Execute Command: {}".format(message))
            for handler in handlers:
                handler.execute_command(self._bot, message)

        @self._bot.message_handler(content_types=['text'])
        def make_response(message):
            for handler in handlers:
                self._bot.send_message(message.chat.id,
                                       handler.make_response(message),
                                       parse_mode="html")

    def run(self):
        log.info("Bot will be started")
        self._bot.polling(none_stop=True)

    def stop(self):
        log.info("Bot will be stopped")
        self._bot.stop_polling()
        # self._bot.stop_bot()


class BotKiller:

    def __init__(self, bot):
        self._bot = bot
        self._stop_now = False
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self._bot.stop()
        self._stop_now = True

    @property
    def stop_now(self):
        return self._stop_now


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
    global log
    log = logging.getLogger("tgbotapp.main")
    config = ConfigParser()
    handlers = []
    try:
        config.read(full_bot_path)
        token = config.get("main", "token")
        names = config.get("main", "handlers").split(",")
        for name in names:
            section = "handler_{}".format(name)
            handler_settings = config.items(section)
            handler_settings = dict(handler_settings)
            unit = import_module(handler_settings.pop("package"))
            handlers.append(unit.msghandler.MessageHandler(**handler_settings))
    except Exception as exc:
        raise exc
    if not handlers:
        raise Exception("No sense to run")

    return CustomTeleBot(token, handlers)


if __name__ == "__main__":
    bot = create_tools()
    killer = BotKiller(bot)
    while True:
        try:
            bot.run()
            break
        except (ConnectionError, ReadTimeout) as exc:
            if killer.stop_now:
                log.error("Bot should be stopped")
                break
            log.error("Error: {}".format(exc))
            sleep(10)
    log.info("Program exit")

import telebot
from . import config


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['trn'])
def handle_start_help(message):
    import pdb
    pdb.set_trace()
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

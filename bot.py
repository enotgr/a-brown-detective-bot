import bot_token
from handlers import main_handlers, help, other_messages_handler
from misc import bot

if __name__ == '__main__':
  bot.polling()

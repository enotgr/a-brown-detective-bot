from misc import bot

def send(message, text):
  bot.send_message(message.chat.id, text, parse_mode='html')

def has_access(user_id):
  return True
  res = user_id == 371659464 or user_id == 694249373
  if not res:
    bot.send_message(user_id, 'Извините, но я вас не узнаю. Предъявите ваше удостоверение.')
  return res

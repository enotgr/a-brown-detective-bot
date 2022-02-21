from misc import bot
from classes.file_service import fileService

def send(message, text):
  bot.send_message(message.chat.id, text, parse_mode='html')

def has_access(user_id):
  res = user_id == 371659464 or user_id == 694249373
  if not res:
    bot.send_message(user_id, 'Извините, но я вас не узнаю. Предъявите ваше удостоверение.')
  return res

def getBack():
    progress = fileService.getJsonObjByPath('state/progress.json')
    thingId = progress['thing']

    if thingId:
      return thingId

    envId = progress['environment']

    if envId:
      return envId

    locationId = progress['location']

    if locationId:
      return 'lookaround'

    return 'location'

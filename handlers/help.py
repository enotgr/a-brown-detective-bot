from misc import bot
from classes.file_service import fileService
from utils.handler_utils import send, has_access

@bot.message_handler(commands=['inventory'])
def inventory(message):
  if not has_access(message.chat.id):
    return

  progress = fileService.getJsonObjByPath('state/progress.json')
  inventoryIds = progress['inventory']

  scene = fileService.getJsonObjByPath('consts/scene.json')

  send(message, '<b><i>Инвентарь:</i></b>\n')

  things = scene['things']

  if len(inventoryIds) == 0:
    send(message, '(Здесь пусто)')
    return

  text = ''

  for thing in things:
    thingId = thing['id']
    if thingId not in inventoryIds:
      continue

    text += '\t- <b>{0}</b>\n\t\t<i>{1}</i>\n\n'.format(thing['title'], thing['description'])

    if len(text) > 500:
      send(message, text)
      text = ''

  if len(text) != 0:
    send(message, text)

@bot.message_handler(commands=['pages'])
def pages(message):
  if not has_access(message.chat.id):
    return

  progress = fileService.getJsonObjByPath('state/progress.json')
  scene = fileService.getJsonObjByPath('consts/scene.json')
  foundPages = progress['found_pages']
  scenePages = scene['pages']
  
  text = '<b>Найденные страницы дневника:</b>\n'

  if not len(foundPages):
    text += '(Здесь пусто)'

  foundPages.sort()

  for scenePage in scenePages:
    if scenePage['id'] not in foundPages:
      continue

    text += '/{0} - {1}\n'.format(scenePage['id'], scenePage['title'])

  send(message, text)

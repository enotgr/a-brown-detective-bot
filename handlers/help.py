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
  
  text = "<b><i>Инвентарь:</i></b>\n"
  things = scene['things']
  isEmpty = True
  for thing in things:
    thingId = thing['id']
    if thingId not in inventoryIds:
      continue
    
    isEmpty = False
    thingText = '\t- <b>{0}</b>\n\t\t<i>{1}</i>\n\n'.format(thing['title'], thing['description'])
    text += thingText

  if isEmpty:
    text += '(Здесь пусто)'

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

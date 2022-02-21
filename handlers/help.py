from misc import bot
from classes.file_service import fileService
from utils.handler_utils import send, has_access, getBack

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

  back = getBack()
  send(message, '/{0} - <i>Назад</i>'.format(back))

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

  if len(foundPages) == len(scenePages):
    text += '\n/coordinates - <i>Координаты</i>\n'

  text += '\n/{0} - <i>Назад</i>'.format(getBack())
  send(message, text)

@bot.message_handler(commands=['coordinates'])
def coordinates(message):
  if not has_access(message.chat.id):
    return

  progress = fileService.getJsonObjByPath('state/progress.json')
  scene = fileService.getJsonObjByPath('consts/scene.json')
  foundPages = progress['found_pages']
  scenePages = scene['pages']

  coordinatesMask = '**.**** ***.***'
  coordinates = ''
  index = 0
  isPageNotFound = False
  for num in coordinatesMask:
    if num == '*':
      scenePage = scenePages[index]
      scenePageId = scenePage['id']
      if scenePageId in foundPages:
        coordinates += scenePage['coord']
      else:
        coordinates += num
        isPageNotFound = True
      index += 1
    else:
      coordinates += num

  if isPageNotFound:
    send(message, '- Чтобы узнать координаты, нужно отыскать все страницы, - подумала детектив.')

  send(message, '<b>Координаты:</b>\n{0}\n\n/{1} - <i>Назад</i>'.format(coordinates, getBack()))

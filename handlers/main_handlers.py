from asyncio.windows_events import NULL
from gc import isenabled
from opcode import haslocal
from misc import bot
from classes.file_service import fileService
from utils.handler_utils import send, has_access

scene_locations = [
  'hall',
  'at_enter',
  'garden',
  'living_room',
  'guest_restroom',
  'kitchen',
  'dining_room',
  'corridor',
  'guest_bedroom',
  'guest_gardrobe',
  'bedroom',
  'workroom',
  'music_room',
]

scene_environments = [
  'safe',
  'commode',
  'flower_bed',
  'oak',
  'fireplace',
  'coffee_table',
  'bookcase',
  'toilet',
  'shower',
  'washbasin',
  'toilet_cabinet',
  'refrigerator',
  'bar_counter',
  'kitchen_cupboard',
  'dinner_table',
  'сouch',
]

@bot.message_handler(commands=['start'])
def send_welcome(message):
  if not has_access(message.chat.id):
    return

  progressState = fileService.getJsonObjByPath('state/progress.json')

  if progressState["started"]:
    send(message, '<i>История уже началась.</i>')
    return

  restart(message)

@bot.message_handler(commands=['restart'])
def restart(message):
  if not has_access(message.chat.id):
    return
  
  initialProgress = fileService.getJsonObjByPath('consts/initial_progress.json')
  initialProgress["started"] = False
  isSaved = fileService.saveJsonFile(initialProgress, 'state/progress.json')

  if not isSaved:
    send(message, 'ERROR: Ошибка сохранения прогресса. Рестарт невозможен.')
    return

  user = message.from_user
  user_name = user.first_name
  if user_name == None:
    user_name = '@{0}'.format(user.username)
  if user_name == None:
    user_name = 'детектив'

  text = 'Привет, {0}!\n\nДобро пожаловать в захватывающую историю, происходящую с <b>детективом Алисой Браун</b>.\n\nТебе предстоит окунуться в мир приключений и загадок и раскрыть одну из самых непростых тайн.\n\n<b>Начнём?</b>\n\n/go - <i>Начать</i>'.format(user_name, bot.get_me())
  send(message, text)

@bot.message_handler(commands=['help'])
def help(message):
  if not has_access(message.chat.id):
    return

  send(message, '/inventory - <i>Инвентарь</i>\n/pages - <i>Найденные страницы дневника</i>')

@bot.message_handler(commands=['go'])
def go(message):
  if not has_access(message.chat.id):
    return

  progressState = fileService.getJsonObjByPath('state/progress.json')

  if progressState['started']:
    send(message, '<i>История уже началась.</i>')
    return

  initialProgress = fileService.getJsonObjByPath('consts/initial_progress.json')
  initialProgress["started"] = True
  isSaved = fileService.saveJsonFile(initialProgress, 'state/progress.json')

  if not isSaved:
    send(message, 'ERROR: Ошибка сохранения прогресса.')
    return

  send(message, '<b>Отлично!</b>\n\n<b>Помни:</b> <i>с помощью команды</i> /help <i>ты всегда можешь посмотреть инвентарь или найденные страницы дневника.</i>\n\n/location - <i>Перейти в стартовую локацию</i>')

@bot.message_handler(commands=['location'])
def location(message):
  if not has_access(message.chat.id):
    return

  progress = fileService.getJsonObjByPath('state/progress.json')

  locationId = progress['location']
  
  scene = fileService.getJsonObjByPath('consts/scene.json')

  currentEnvId = progress["environment"]
  currentThingId = progress["thing"]
  if currentEnvId != '':
    if currentThingId == '':      
      send(message, 'Сейчас недоступно.\n/lookaround - Осмотреться')
      return

    envs = scene["environments"]
    currentEnv = NULL
    isEnvFound = False
    
    for env in envs:
      id = env["id"]    
      if id not in currentEnvId:
        continue
     
      isEnvFound = True
      currentEnv = env
      break
    
    if not isEnvFound:
      send(message, 'ERROR: Ничего нет')
      return
    
    send(message, 'Сейчас недоступно.\n/{0} - Назад'.format(currentEnv["id"]))
    return
  
  text = ''
  isLocationFound = False
  locations = scene["locations"]
  locationIds = []
  currentLocation = NULL
  
  for loc in locations:
    id = loc["id"]    
    locationIds.append(id)
    
    if id != locationId:
      continue
    
    isLocationFound = True
    currentLocation = loc
  
  if not isLocationFound:
    send(message, 'ERROR: (Не найдено в списке локаций)')
    return
  
  title = currentLocation["title"]
  description = currentLocation["description"]
    
  availableLocationIds = currentLocation["available_locations"]
  availableLocationsText = "Можно перейти в:\n"
  hasAvailableLocations = False

  for locId in availableLocationIds:
    if locId not in locationIds:
      continue
      
    hasAvailableLocations = True
    loc = locations[locationIds.index(locId)]
    availableLocationsText += '/{0} - {1}\n'.format(locId, loc["title"])

  if not hasAvailableLocations:
    availableLocationsText = "Выхода нет.\n"
    
  text = '<b><i>{0}</i></b>\n\t{1} {2}\n/lookaround - Осмотреться'.format(title, description, availableLocationsText)
    
  send(message, 'Текущая локация: {0}'.format(text))

@bot.message_handler(commands=scene_locations)
def goto(message):
  if not has_access(message.chat.id):
    return

  progress = fileService.getJsonObjByPath('state/progress.json')
  scene = fileService.getJsonObjByPath('consts/scene.json')
  
  currentEnvId = progress["environment"]
  currentThingId = progress["thing"]
  
  if currentEnvId != '':
    if currentThingId == '':
      send(message, 'Сейчас недоступно.\n/lookaround - Осмотреться')
      return
    
    envs = scene["environments"]
    currentEnv = NULL
    isEnvFound = False
    
    for env in envs:
      id = env["id"]    
      if id not in currentEnvId:
        continue
     
      isEnvFound = True
      currentEnv = env
      break
    
    if not isEnvFound:
      send(message, 'ERROR: Ничего нет')
      return
    
    send(message, 'Сейчас недоступно.\n/{0} - Назад'.format(currentEnv["id"]))
    return

  currentLocationId = progress['location']
  locations = scene["locations"]
  currentLocation = NULL
  hasLocation = False

  for loc in locations:
    id = loc["id"]
    if currentLocationId != id:
      continue

    hasLocation = True      
    currentLocation = loc
    break

  if not hasLocation:
    send(message, 'ERROR: Такой локации нет.\n')
    return

  availableLocationIds = currentLocation["available_locations"]
  targetLocationId = message.text.replace('/', '')

  if targetLocationId not in availableLocationIds and targetLocationId != progress['location']:
    send(message, 'Эта локация недоступна отсюда.\n')
    return

  progress['location'] = targetLocationId
  visitedLocations = progress['visited_locations']

  if targetLocationId not in visitedLocations:
    visitedLocations.append(targetLocationId)
    progress['visited_locations'] = visitedLocations

  isSaved = fileService.saveJsonFile(progress, 'state/progress.json')
  if not isSaved:
    send(message, 'ERROR: Ошибка сохранения прогресса.')
    return

  location(message)

@bot.message_handler(commands=['lookaround'])
def lookaround(message):
  if not has_access(message.chat.id):
    return

  progress = fileService.getJsonObjByPath('state/progress.json')
  locationId = progress['location']

  scene = fileService.getJsonObjByPath('consts/scene.json')

  text = '<i><b>Вокруг Алиса видит:</b></i>\n'
  isLocationFound = False
  locationIds = []
  currentLocation = NULL

  locations = scene["locations"]
  for loc in locations:
    id = loc["id"]    
    locationIds.append(id)

    if id != locationId:
      continue

    isLocationFound = True
    currentLocation = loc
    break

  if not isLocationFound:
    send(message, 'ERROR: Неправильная текущая локация')
    return

  envIds = currentLocation["environment"]    
  envs = scene["environments"]
  currentEnv = NULL
  isEnvFound = False
    
  for env in envs:
    id = env["id"]    
    if id not in envIds:
      continue
     
    isEnvFound = True
    currentEnv = env
    text += '/{0} - {1}\n'.format(id, env["title"])
   
  if not isEnvFound:
    send(message, '(Здесь пусто)\n\n/location - Назад')
    return

  currentThingId = progress["thing"]
  if currentThingId != '':
    send(message, 'Сейчас недоступно.\n\n/{0} - Назад'.format(currentEnv["id"]))
    return

  text += "\n/location - Назад"

  progress["environment"] = ''
  progress["thing"] = ''

  isSaved = fileService.saveJsonFile(progress, 'state/progress.json')

  if not isSaved:
    send(message, 'ERROR: Ошибка сохранения прогресса.')
    return

  send(message, text)

@bot.message_handler(commands=scene_environments)
def exploreEnv(message):
  if not has_access(message.chat.id):
    return

  targetEnvId = message.text.replace('/', '')

  progress = fileService.getJsonObjByPath('state/progress.json')
  scene = fileService.getJsonObjByPath('consts/scene.json')
  currentLocationId = progress['location']

  isLocationFound = False
  locationIds = []
  currentLocation = NULL

  locations = scene["locations"]
  for loc in locations:
    id = loc["id"]    
    locationIds.append(id)

    if id != currentLocationId:
      continue

    isLocationFound = True
    currentLocation = loc
    break

  if not isLocationFound:
    send(message, 'ERROR: Текущая локация не найдена.')
    return

  if targetEnvId not in currentLocation["environment"]:
    send(message, 'Этот предмет сейчас недоступен.\n\n/lookaround - Назад')
    return

  envs = scene['environments']
  targetEnv = NULL
  hasEnv = False

  for env in envs:
    id = env["id"]
    if targetEnvId != id:
      continue

    hasEnv = True      
    targetEnv = env
    break

  if not hasEnv:
    send(message, 'ERROR: Такое окружение не найдено.\n')
    return

  progress['environment'] = targetEnvId
  progress['thing'] = ''

  thingsText = '\nЗдесь есть:\n'
  targetEnvThingIds = targetEnv['things']
  targetEnvPageIds = targetEnv['pages']
  openedEnvs = progress['opened_environments']

  isSaved = fileService.saveJsonFile(progress, 'state/progress.json')
  if not isSaved:
    send(message, 'ERROR: Ошибка сохранения прогресса.')
    return

  if targetEnv['is_closed'] and targetEnvId not in openedEnvs:
    hint = targetEnv['hint']
    send(message, '{0}\n\n/lookaround - Назад'.format(hint))
    return
  
  if targetEnvId not in openedEnvs:
    openedEnvs.append(targetEnvId)
    progress['opened_environments'] = openedEnvs

  isSaved = fileService.saveJsonFile(progress, 'state/progress.json')
  if not isSaved:
    send(message, 'ERROR: Ошибка сохранения прогресса.')
    return

  inventory = progress['inventory']
  things = scene['things']

  hasSomething = False

  for thing in things:
    id = thing['id']

    if id in inventory or id not in targetEnvThingIds:
      continue

    hasSomething = True
    thingsText += '/{0} - {1}\n'.format(thing['id'], thing['title'])

  foundPages = progress['found_pages']
  pages = scene['pages']

  for page in pages:
    id = page['id']

    if id in foundPages or id not in targetEnvPageIds:
      continue

    hasSomething = True
    thingsText += '/{0} - {1}\n'.format(page['id'], page['title'])

  if not hasSomething:
    thingsText = '\n(Здесь пусто)\n'

  send(message, '<i><b>{0}</b></i>.{1}\n/lookaround - Назад'.format(targetEnv['title'], thingsText))

@bot.message_handler(commands=['socks', 'cover', 'leyka', 'red_flower', 'acorn', 'firewood', 'magazine', 'book_1', 'book_2', 'book_3', 'book_4', 'board_game'])
def exploreThing(message):
  if not has_access(message.chat.id):
    return
  
  targetThingId = message.text.replace('/', '')
  
  progress = fileService.getJsonObjByPath('state/progress.json')
  scene = fileService.getJsonObjByPath('consts/scene.json')
  
  currentLocationId = progress['location']
  isLocationFound = False
  locationIds = []
  
  things = scene["things"]
  inventory = progress["inventory"]
  for thing in things:
    if thing['id'] == targetThingId and targetThingId in inventory:
      send(message, "<i><b>{0}</b></i>: {1}\n\n".format(thing["title"], thing["description"]))
      return
  
  locations = scene["locations"]
  for loc in locations:
    id = loc["id"]    
    locationIds.append(id)
    
    if id != currentLocationId:
      continue
    
    isLocationFound = True
    break
  
  if not isLocationFound:
    send(message, 'ERROR: Текущая локация не найдена.')
    return
  
  currentEnvId = progress['environment']
  if currentEnvId == '':
    send(message, "Сейчас этот предмет недоступен.\n/location - Назад")
    return
  
  isEnvFound = False
  envIds = []
  currentEnv = NULL
  
  envs = scene["environments"]
  for env in envs:
    id = env["id"]    
    envIds.append(id)
    
    if id != currentEnvId:
      continue
    
    isEnvFound = True
    currentEnv = env
    break
  
  if not isEnvFound:
    send(message, 'ERROR: Текущее место осмотра не найдено.')
    return
  
  currentEnvThings = currentEnv["things"]
  hasThing = False
  targetThing = NULL
  
  for thing in things:
    id = thing["id"]
    if id not in currentEnvThings or id != targetThingId:
      continue
    
    hasThing = True
    targetThing = thing
    break
  
  if not hasThing:
    send(message, "Сейчас этот предмет недоступен.\n/{0} - Назад".format(currentEnv["id"]))
    return
  
  progress["thing"] = targetThingId
  
  isSaved = fileService.saveJsonFile(progress, 'state/progress.json')
  if not isSaved:
    send(message, '- Не могу поднять этот предмет.')
    return
  
  send(message, "<i><b>{0}</b></i>: {1}\n\n/take - Взять\n/{2} - Назад".format(targetThing["title"], targetThing["description"], currentEnv["id"]))

@bot.message_handler(commands=['take'])
def takeThing(message):
  if not has_access(message.chat.id):
    return
  
  progress = fileService.getJsonObjByPath('state/progress.json')
  currentThing = progress['thing']
  
  if not currentThing:
    send(message, '- Мои руки чисты, - подумала Алиса.')
    return
  
  inventory = progress['inventory']
  inventory.append(currentThing)
  progress['inventory'] = inventory
  progress['thing'] = ''
  isSaved = fileService.saveJsonFile(progress, 'state/progress.json')

  if not isSaved:
    send(message, '- Я не могу сейчас это взять.')
    return

  envObj = progress['environment']
  
  send(message, '- Возможно, мне это пригодится, - подумала Алиса.\n\n/{0} - Назад'.format(envObj))
  
@bot.message_handler(commands=['page_1', 'page_2', 'page_3', 'page_4', 'page_5'])
def takePage(message):
  if not has_access(message.chat.id):
    return
  
  targetPageId = message.text.replace('/', '')

  progress = fileService.getJsonObjByPath('state/progress.json')
  scene = fileService.getJsonObjByPath('consts/scene.json')
  foundPageIds = progress['found_pages']
  scenePages = scene['pages']
  scenePage = NULL
  
  for page in scenePages:
    if page['id'] == targetPageId:
      scenePage = page
      break

  if targetPageId in foundPageIds:
    text = '<i>{0}</i>\n<b>{1}</b>\n\n'.format(scenePage['title'], scenePage['date'])
    text += fileService.getTextFileByPath('pages/{0}.txt'.format(targetPageId))
    text += '\n/pages - Назад'
    send(message, text)
    return

  currEnvId = progress['environment']
  if not currEnvId:
    send(message, 'ERROR: осматриваемый предмет не обнаружен.')
    return

  sceneEnv = scene['environments']

  envPages = []

  for env in sceneEnv:
    if currEnvId == env['id']:
      envPages = env['pages']
      break;

  if targetPageId in envPages:
    progress['found_pages'].append(targetPageId)
    isSaved = fileService.saveJsonFile(progress, 'state/progress.json')
    if not isSaved:
      send(message, 'ERROR: не могу взять эту страницу.')
      return

    text = '<i>{0}</i>\n<b>{1}</b>\n\n'.format(scenePage['title'], scenePage['date'])
    text += fileService.getTextFileByPath('pages/{0}.txt'.format(targetPageId))
    text += '\n/{0} - Назад'.format(currEnvId)
    send(message, text)
    return

  send(message, '404: страница не найдена.')
  return

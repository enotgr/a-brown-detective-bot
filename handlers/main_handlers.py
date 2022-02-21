import time
from misc import bot
from classes.file_service import fileService
from utils.handler_utils import send, has_access, getBack
from consts.scene_commands import scene_locations, scene_environments, scene_things

@bot.message_handler(commands=['start'])
def send_welcome(message):
  if not has_access(message.chat.id):
    return

  progressState = fileService.getJsonObjByPath('state/progress.json')

  if progressState['started']:
    send(message, '<i>История уже началась.</i>')
    return

  restart(message)

@bot.message_handler(commands=['restart'])
def restart(message):
  if not has_access(message.chat.id):
    return

  initialProgress = fileService.getJsonObjByPath('consts/initial_progress.json')
  initialProgress['started'] = False
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

  send(message, '/inventory - <i>Инвентарь</i>\n/pages - <i>Найденные страницы дневника</i>\n/location - <i>Текущая локация</i>\n/lookaround - <i>Осмотреться</i>')

@bot.message_handler(commands=['go'])
def go(message):
  if not has_access(message.chat.id):
    return

  progressState = fileService.getJsonObjByPath('state/progress.json')

  if progressState['started']:
    send(message, '<i>История уже началась.</i>')
    return

  initialProgress = fileService.getJsonObjByPath('consts/initial_progress.json')
  initialProgress['started'] = True
  isSaved = fileService.saveJsonFile(initialProgress, 'state/progress.json')

  if not isSaved:
    send(message, 'ERROR: Ошибка сохранения прогресса.')
    return

  bot.send_chat_action(message.chat.id, 'typing')
  time.sleep(1)
  send(message, '<b>Отлично!</b>\n\n<b>Помни:</b> <i>с помощью команды</i> /help <i>ты всегда можешь посмотреть инвентарь или найденные страницы дневника.</i>\n\n')

  bot.send_chat_action(message.chat.id, 'typing')
  start_text = fileService.getTextFileByPath('consts/start_text.txt')
  time.sleep(1)
  send(message, start_text)
  
  bot.send_chat_action(message.chat.id, 'typing')
  time.sleep(7)
  send(message, '<i>Новое входящее письмо:</i>\n\t\tНомер Робба: +47 (409) 942 96 58\n\n\t\tМэтью: +47 (409) 525 44 70\n\t\tАдрес дома: Kirkegata st. 37\n\n/location - <i>Перейти в стартовую локацию</i>')

@bot.message_handler(commands=['location'])
def location(message):
  if not has_access(message.chat.id):
    return

  progress = fileService.getJsonObjByPath('state/progress.json')
  scene = fileService.getJsonObjByPath('consts/scene.json')

  locationId = progress['location']

  visitedLocations = progress['visited_locations']
  isFirst = False

  if locationId not in visitedLocations:
    visitedLocations.append(locationId)
    progress['visited_locations'] = visitedLocations
    isFirst = True

  isSaved = fileService.saveJsonFile(progress, 'state/progress.json')
  if not isSaved:
    send(message, 'ERROR: Ошибка сохранения прогресса.')
    return

  currentEnvId = progress['environment']
  currentThingId = progress['thing']
  if currentEnvId != '':
    if currentThingId == '':
      send(message, 'Сейчас недоступно.\n\n/{0} - <i>Назад</i>'.format(getBack()))
      return

    envs = scene['environments']
    isEnvFound = False

    for env in envs:
      id = env['id']
      if id not in currentEnvId:
        continue

      isEnvFound = True
      break

    if not isEnvFound:
      send(message, 'ERROR: Ничего нет')
      return

    send(message, 'Сейчас недоступно.\n\n/{0} - <i>Назад</i>'.format(getBack()))
    return

  text = ''
  isLocationFound = False
  locations = scene['locations']
  locationIds = []
  currentLocation = None

  for loc in locations:
    id = loc['id']
    locationIds.append(id)

    if id != locationId:
      continue

    isLocationFound = True
    currentLocation = loc

  if not isLocationFound:
    send(message, 'ERROR: (Не найдено в списке локаций)')
    return

  title = currentLocation['title']
  description = currentLocation['description']
  firstDescription = currentLocation['first']

  availableLocationIds = currentLocation['available_locations']
  availableLocationsText = 'Доступные локации:\n'
  hasAvailableLocations = False

  for locId in availableLocationIds:
    if locId not in locationIds:
      continue

    hasAvailableLocations = True
    loc = locations[locationIds.index(locId)]
    availableLocationsText += '/{0} - {1}\n'.format(locId, loc['title'])

  if not hasAvailableLocations:
    availableLocationsText = 'Выхода нет.\n'

  if isFirst and firstDescription:
    send(message, firstDescription)

  text = '{0}\n\nТекущая локация: <b><i>{1}</i></b>\n\n{2}\n/lookaround - <i>Осмотреться</i>'.format(description, title, availableLocationsText)

  send(message, text)

@bot.message_handler(commands=scene_locations)
def goto(message):
  if not has_access(message.chat.id):
    return

  progress = fileService.getJsonObjByPath('state/progress.json')
  scene = fileService.getJsonObjByPath('consts/scene.json')

  currentEnvId = progress['environment']
  currentThingId = progress['thing']

  if currentEnvId != '':
    if currentThingId == '':
      send(message, 'Сейчас недоступно.\n\n/{0} - <i>Назад</i>'.format(getBack()))
      return

    envs = scene['environments']
    isEnvFound = False

    for env in envs:
      id = env['id']
      if id not in currentEnvId:
        continue

      isEnvFound = True
      break

    if not isEnvFound:
      send(message, 'ERROR: Ничего нет')
      return

    send(message, 'Сейчас недоступно.\n\n/{0} - <i>Назад</i>'.format(getBack()))
    return

  currentLocationId = progress['location']
  locations = scene['locations']
  currentLocation = None
  hasLocation = False

  for loc in locations:
    id = loc['id']
    if currentLocationId != id:
      continue

    hasLocation = True
    currentLocation = loc
    break

  if not hasLocation:
    send(message, 'ERROR: Такой локации нет.\n')
    return

  availableLocationIds = currentLocation['available_locations']
  targetLocationId = message.text.replace('/', '')

  if targetLocationId not in availableLocationIds and targetLocationId != progress['location']:
    send(message, 'Эта локация недоступна отсюда.\n\n/{0} - <i>Назад</i>'.format(getBack()))
    return

  inventory = progress['inventory']
  targetLocation = None

  for loc in locations:
    id = loc['id']
    if targetLocationId == id:
      targetLocation = loc
      break

  text = ''
  if targetLocation['is_closed'] == True and len(targetLocation['keys']) > 0:
    keys = targetLocation['keys']
    for key in keys:
      if key not in inventory:
        text += '<i>Для доступа в эту локацию нужно найти:</i>\n'
        for thing in scene['things']:
          if thing['id'] == key:
            text += '/{0} - <i>{1}</i>\n'.format(key, thing['title'])
            break
        text += '\n/inventory - <i>Инвентарь</i>\n/location - <i>Назад</i>'
        send(message, text)
  if len(text) != 0:
    return

  progress['location'] = targetLocationId

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
  currentLocation = None

  locations = scene['locations']
  for loc in locations:
    id = loc['id']
    locationIds.append(id)

    if id != locationId:
      continue

    isLocationFound = True
    currentLocation = loc
    break

  if not isLocationFound:
    send(message, 'ERROR: Неправильная текущая локация')
    return

  envIds = currentLocation['environment']
  envs = scene['environments']
  currentEnv = None
  isEnvFound = False

  for env in envs:
    id = env['id']
    if id not in envIds:
      continue

    isEnvFound = True
    currentEnv = env
    text += '/{0} - {1}\n'.format(id, env['title'])

  if not isEnvFound:
    send(message, '(Здесь пусто)\n\n/location - <i>Назад</i>')
    return

  currentThingId = progress['thing']
  if currentThingId != '':
    send(message, 'Сейчас недоступно.\n\n/{0} - <i>Назад</i>'.format(getBack()))
    return

  text += '\n/location - <i>Назад</i>'

  progress['environment'] = ''
  progress['thing'] = ''

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
  currentLocation = None

  locations = scene['locations']
  for loc in locations:
    id = loc['id']
    locationIds.append(id)

    if id != currentLocationId:
      continue

    isLocationFound = True
    currentLocation = loc
    break

  if not isLocationFound:
    send(message, 'ERROR: Текущая локация не найдена.')
    return

  if targetEnvId not in currentLocation['environment']:
    send(message, 'Сейчас недоступно.\n\n/{0} - <i>Назад</i>'.format(getBack()))
    return

  envs = scene['environments']
  targetEnv = None
  hasEnv = False

  for env in envs:
    id = env['id']
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
    send(message, '{0}\n\n/lookaround - <i>Назад</i>'.format(hint))
    return

  isFirst = False

  if targetEnvId not in openedEnvs:
    openedEnvs.append(targetEnvId)
    progress['opened_environments'] = openedEnvs
    isFirst = True

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

  if isFirst and targetEnv['first']:
    send(message, targetEnv['first'])

  send(message, '<i><b>{0}</b></i>.{1}\n/lookaround - <i>Назад</i>'.format(targetEnv['title'], thingsText))

@bot.message_handler(commands=scene_things)
def exploreThing(message):
  if not has_access(message.chat.id):
    return

  targetThingId = message.text.replace('/', '')

  progress = fileService.getJsonObjByPath('state/progress.json')
  scene = fileService.getJsonObjByPath('consts/scene.json')

  currentLocationId = progress['location']
  isLocationFound = False
  locationIds = []

  things = scene['things']
  inventory = progress['inventory']
  for thing in things:
    if thing['id'] == targetThingId and targetThingId in inventory:
      # пасхалка
      if progress['location'] == 'garden':
        if targetThingId == 'acorn':
          progress['tree'] = True
        elif targetThingId == 'leyka' and progress['tree']:
          send(message, '- Я посадила дерево, - сказала Алиса.')
          progress['tree'] = False
          fileService.saveJsonFile(progress, 'state/progress.json')
          return
        else:
          progress['tree'] = False
        fileService.saveJsonFile(progress, 'state/progress.json')
      # конец пасхалки
      send(message, '<i><b>{0}</b></i>: {1}\n\n/{2} - <i>Назад</i>'.format(thing['title'], thing['description'], getBack()))
      return

  locations = scene['locations']
  for loc in locations:
    id = loc['id']
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
    send(message, 'Сейчас этот предмет недоступен.\n\n/{0} - <i>Назад</i>'.format(getBack()))
    return

  isEnvFound = False
  envIds = []
  currentEnv = None

  envs = scene['environments']
  for env in envs:
    id = env['id']
    envIds.append(id)

    if id != currentEnvId:
      continue

    isEnvFound = True
    currentEnv = env
    break

  if not isEnvFound:
    send(message, 'ERROR: Текущее место осмотра не найдено.')
    return

  currentEnvThings = currentEnv['things']
  hasThing = False
  targetThing = None

  for thing in things:
    id = thing['id']
    if id not in currentEnvThings or id != targetThingId:
      continue

    hasThing = True
    targetThing = thing
    break

  if not hasThing:
    send(message, 'Сейчас недоступно.\n\n/{0} - <i>Назад</i>'.format(getBack()))
    return

  progress['thing'] = targetThingId

  isSaved = fileService.saveJsonFile(progress, 'state/progress.json')
  if not isSaved:
    send(message, '- Не могу поднять этот предмет.')
    return

  send(message, '<i><b>{0}</b></i>.\n{1}\n\n/take - <i>Взять</i>\n/{2} - <i>Назад</i>'.format(targetThing['title'], targetThing['description'], currentEnv['id']))

@bot.message_handler(commands=['take'])
def takeThing(message):
  if not has_access(message.chat.id):
    return

  progress = fileService.getJsonObjByPath('state/progress.json')
  currentThing = progress['thing']

  if not currentThing:
    send(message, '- Мои руки чисты, - подумала Алиса.\n\n/{0} - <i>Назад</i>'.format(getBack()))
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

  send(message, '- Возможно, мне это пригодится, - подумала Алиса.\n\n/{0} - <i>Назад</i>'.format(envObj))

@bot.message_handler(commands=['page_1', 'page_2', 'page_3', 'page_4', 'page_5', 'page_6', 'page_7', 'page_8', 'page_9', 'page_10', 'page_11', 'page_12'])
def takePage(message):
  if not has_access(message.chat.id):
    return

  targetPageId = message.text.replace('/', '')

  progress = fileService.getJsonObjByPath('state/progress.json')
  scene = fileService.getJsonObjByPath('consts/scene.json')
  foundPageIds = progress['found_pages']
  scenePages = scene['pages']
  scenePage = None

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
    send(message, '404: страница не найдена.\n\n{0} - <i>Назад</i>'.format(getBack()))
    return

  sceneEnv = scene['environments']

  envPages = []

  for env in sceneEnv:
    if currEnvId == env['id']:
      envPages = env['pages']
      break;

  if targetPageId in envPages:
    foundPages = progress['found_pages']
    foundPages.append(targetPageId)
    progress['found_pages'] = foundPages
    isSaved = fileService.saveJsonFile(progress, 'state/progress.json')
    if not isSaved:
      send(message, 'ERROR: не могу взять эту страницу.')
      return

    text = '<i>{0}</i>\n<b>{1}</b>\n\n'.format(scenePage['title'], scenePage['date'])
    text += fileService.getTextFileByPath('pages/{0}.txt'.format(targetPageId))
    text += '\n<i>На обратной стороне страницы нарисована цифра: <b>{0}</b>.</i>\n'.format(scenePage['coord'])
    
    if len(foundPages) == len(scenePages):
      text += '\n- Теперь все страницы у меня, я могу узнать координаты, - сказала Алиса.\n/coordinates - <i>Координаты</i>\n'

    text += '\n/pages - <i>Найденные страницы</i>\n/{0} - <i>Назад</i>'.format(currEnvId)
    send(message, text)
    return

  send(message, 'ERROR: осматриваемый предмет не обнаружен.')
  return

from asyncio.windows_events import NULL
from misc import bot
from classes.file_service import fileService
from utils.handler_utils import send, has_access

@bot.message_handler()
def otherMessagesHandler(message):
  if not has_access(message.chat.id):
    return
  
  progress = fileService.getJsonObjByPath('state/progress.json')
  scene = fileService.getJsonObjByPath('consts/scene.json')
  currEnvId = progress['environment']
  
  if not currEnvId:
    return
  
  environments = scene['environments']
  currEnv = NULL
  
  for env in environments:
    if env['id'] == currEnvId:
      currEnv = env
      break

  openedEnvs = progress['opened_environments']

  if currEnvId not in openedEnvs:
    if currEnv['password'] == message.text:
      openedEnvs.append(currEnvId)
      progress['opened_environments'] = openedEnvs

      isSaved = fileService.saveJsonFile(progress, 'state/progress.json')
      if not isSaved:
        send(message, 'ERROR: Ошибка сохранения прогресса.')
        return

      send(message, currEnv['opened'])
    else:
      send(message, 'Этот пароль не подходит.\n\n/lookaround - Назад')

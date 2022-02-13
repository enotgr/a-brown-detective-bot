from asyncio.windows_events import NULL
from consts import world
import json

class FileService:
  def getJsonObjByPath(self, path):
    jsonFile = NULL
    
    try:
      file = open(path, 'r', encoding='utf-8')
      jsonFile = json.load(file)
      file.close()
    except:
      print("Error: can't open progress file.")
    return jsonFile

  def saveJsonFile(self, jsonObj, path):
    try:
      file = open(path, 'w', encoding='utf-8')
      json.dump(jsonObj, file, indent = 2)
      file.close()
      return True
    except:
      print("Error: can't save progress file.")
      return False
    
  def getTextFileByPath(self, path):
    text = ''
    try:
      file = open(path, 'r', encoding='utf-8')
      text = file.read();
    except:
      print("Error: can't read file.")
    return text

fileService = FileService()

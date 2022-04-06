import clr
import sys
import json
import os
import ctypes
import codecs
import time

ScriptName = "Minijogo de quiz, perguntas e respostas"
Website = "http://www.twitch.tv/ElitonK"
Description = "Quiz Minijogo para Streamlabs Bot"
Creator = "ElitonK"
Version = "1.3.3"

configFile = "config.json"
questionsFile = "perguntas.txt"
settings = {}
path = ""

questionsList = []
currentQuestion = ""
currentAnswers = []
currentReward = 0

resetTime = 0


def ScriptToggled(state):
	return

def Init():
	global questionsList, settings, path 

	path = os.path.dirname(__file__)
	try:
		with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
			settings = json.load(file, encoding='utf-8-sig')
	except:
		settings = {
			"liveOnly": True,
			"permission": "Everyone",
			"ignoreCaseSensitivity": True,
			"newQuestionOnAnswer" : False,
			"separator": "##",  
			"minReward": 1,
			"maxReward": 10,
			"minQuestionInterval": 10,			
			"maxQuestionInterval": 20,			
			"responseAnnouncement": "Ganhe $recompensa $moeda respondendo: $pergunta",
			"responseWon": "$user respondeu a pergunta primeiro dizendo $resposta E GANHOU $recompensa $moeda!",
			"showRightAnswer": True,
			"responseNobody": "A resposta certa para: $pergunta | ERA: $resposta"
		}

	questionsLocation = os.path.join(path, questionsFile)

	try: 
		with codecs.open(questionsLocation, encoding="utf-8-sig", mode="r") as file:
			questionsList = [[word.strip() for word in line.split(settings["separator"])] for line in file if line.strip()]
	except:
		if os.path.isfile(questionsLocation):
			questionsList = ["Se voce esta vendo esta mensagem, salve o arquivo como UTF-8"]
		else: 
			with codecs.open(questionsLocation, encoding="utf-8-sig", mode="w+") as file:
				file.write('Qual eh a cor da grama? ' + settings['separator'] + ' verde\r\n')
				file.write('O que tem entre o 1 e o 3? ' + settings['separator'] + ' 2 ' + settings['separator'] + ' dois')
				questionsList = [['Abra seu arquivo "perguntas.txt" para adicionar suas proprias perguntas', '_']]
	
	return

def Execute(data):
	global currentQuestion, currentAnswers, currentReward, resetTime

	if data.IsChatMessage() and ((data.Message in currentAnswers) or (settings["ignoreCaseSensitivity"] and (data.Message.lower() in [a.lower() for a in currentAnswers]))) and Parent.HasPermission(data.User, settings["permission"], "") and ((settings["liveOnly"] and Parent.IsLive()) or (not settings["liveOnly"])):
		userId = data.User			
		username = data.UserName

		Parent.AddPoints(userId, username, currentReward)

		outputMessage = settings["responseWon"]	

		outputMessage = outputMessage.replace("$user", username)
		outputMessage = outputMessage.replace("$pergunta", currentQuestion)
		outputMessage = outputMessage.replace("$resposta", data.Message.title())
		outputMessage = outputMessage.replace("$recompensa", str(currentReward))
		outputMessage = outputMessage.replace("$moeda", Parent.GetCurrencyName())

		currentQuestion = ""
		currentAnswers = []
		currentReward = 0

		if settings["newQuestionOnAnswer"]:
			resetTime = time.time()	+ 10

		Parent.SendStreamMessage(outputMessage)
	return

def ReloadSettings(jsonData):
	Init()
	return

def OpenReadMe():
	location = os.path.join(os.path.dirname(__file__), "LEIAME.txt")
	os.startfile(location)
	return

def OpenQuestionsFile():
	location = os.path.join(os.path.dirname(__file__), questionsFile)
	os.startfile(location)
	return


def Tick():
	global questionsList, resetTime, currentQuestion, currentAnswers, currentReward

	if (settings["liveOnly"] and Parent.IsLive()) or (not settings["liveOnly"]):
		currentTime = time.time()

		if(currentTime >= resetTime):
			resetTime = currentTime + Parent.GetRandom((settings["minQuestionInterval"] * 60), (settings["maxQuestionInterval"] * 60) + 1)
		
			if settings["showRightAnswer"] and (len(currentAnswers) != 0):
				outputMessage = settings["responseNobody"]
				outputMessage = outputMessage.replace("$pergunta", currentQuestion)
				outputMessage = outputMessage.replace("$resposta", currentAnswers[0])
				Parent.SendStreamMessage(outputMessage)

			outputMessage = settings["responseAnnouncement"]

			randomQuestion = questionsList.pop(Parent.GetRandom(0, len(questionsList)))
			currentQuestion = randomQuestion.pop(0) 
			currentAnswers = randomQuestion

			if len(questionsList) == 0:
				try: 
					with codecs.open(os.path.join(path, questionsFile), encoding="utf-8-sig", mode="r") as file:
						questionsList = [[word.strip() for word in line.split(settings["separator"])] for line in file if line.strip()]
				except:
					questionsList = [["Se voce esta vendo esta mensagem, salve o arquivo como UTF-8","Error"]]

			currentReward = Parent.GetRandom(settings["minReward"], settings["maxReward"])
			outputMessage = outputMessage.replace("$pergunta", currentQuestion)
			outputMessage = outputMessage.replace("$recompensa", str(currentReward))
			outputMessage = outputMessage.replace("$moeda", Parent.GetCurrencyName())

			Parent.SendStreamMessage(outputMessage)
	return

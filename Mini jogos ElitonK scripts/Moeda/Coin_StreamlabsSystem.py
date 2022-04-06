import clr
import sys
import json
import os
import ctypes
import codecs

ScriptName = "Mini jogo da moeda"
Website = "http://www.twitch.tv/ElitonK"
Description = "Moeda Mini jogo para Streamlabs Bot em portugues"
Creator = "ElitonK"
Version = "1.2.4"

configFile = "config.json"
settings = {}

def ScriptToggled(state):
	return

def Init():
	global settings

	path = os.path.dirname(__file__)
	try:
		with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
			settings = json.load(file, encoding='utf-8-sig')
	except:
		settings = {
			"liveOnly": True,
			"command": "!moeda",
			"permission": "Everyone",
			"useCustomCosts" : True,
			"costs": 1,
			"reward": 2,
			"emoteWon" : "VoteYea",
			"emoteLost" : "VoteNay",
			"useCooldown": True,
			"useCooldownMessages": True,
			"cooldown": 1,
			"onCooldown": "$user, $comando esta em tempo de espera, recarregando em $cd minutos!",
			"userCooldown": 300,
			"onUserCooldown": "$user, $comando ta recarregando por $cd minutos pra voce!",
			"responseNotEnoughPoints": "$user ce so tem $pontos $moeda pra jogar a moeda.",
			"responseWon": "$$user jogou a moeda $ganhou e ganhou $recompensa $moeda",
			"responseLost": "$user jogou a moeda $perdeu e perdeu $recompensa $moeda"
		}

def Execute(data):
	if data.IsChatMessage() and data.GetParam(0).lower() == settings["command"] and Parent.HasPermission(data.User, settings["permission"], "") and ((settings["liveOnly"] and Parent.IsLive()) or (not settings["liveOnly"])):
		outputMessage = ""
		userId = data.User			
		username = data.UserName
		points = Parent.GetPoints(userId)

		if settings["useCustomCosts"] and (data.GetParamCount() == 2):
			try: 
				costs = int(data.GetParam(1))
			except:
				if data.GetParam(1) == 'all': 
					costs = points
				else :
					costs = settings["costs"] 
		else:
			costs = settings["costs"]

		if (costs > Parent.GetPoints(userId)) or (costs < 1):
			outputMessage = settings["responseNotEnoughPoints"]
		elif settings["useCooldown"] and (Parent.IsOnCooldown(ScriptName, settings["command"]) or Parent.IsOnUserCooldown(ScriptName, settings["command"], userId)):
			if settings["useCooldownMessages"]:
				if Parent.GetCooldownDuration(ScriptName, settings["command"]) > Parent.GetUserCooldownDuration(ScriptName, settings["command"], userId):
					cdi = Parent.GetCooldownDuration(ScriptName, settings["command"])
					cd = str(cdi / 60) + ":" + str(cdi % 60).zfill(2) 
					outputMessage = settings["onCooldown"]
				else:
					cdi = Parent.GetUserCooldownDuration(ScriptName, settings["command"], userId)
					cd = str(cdi / 60) + ":" + str(cdi % 60).zfill(2) 
					outputMessage = settings["onUserCooldown"]
				outputMessage = outputMessage.replace("$cd", cd)
			else:
				outputMessage = ""
		else:
			Parent.RemovePoints(userId, username, costs)

			coin = Parent.GetRandom(0, 2)
			reward = ""

			if coin == 0:
				outputMessage = (settings["responseWon"])
				reward = costs * settings["reward"]
				Parent.AddPoints(userId, username, int(reward))
			else:
				outputMessage = settings["responseLost"]
				reward = costs

			outputMessage = outputMessage.replace("$recompensa", str(reward))

			if settings["useCooldown"]:
				Parent.AddUserCooldown(ScriptName, settings["command"], userId, settings["userCooldown"])
				Parent.AddCooldown(ScriptName, settings["command"], settings["cooldown"])

		outputMessage = outputMessage.replace("$custo", str(costs))
		outputMessage = outputMessage.replace("$user", username)
		outputMessage = outputMessage.replace("$pontos", str(points))
		outputMessage = outputMessage.replace("$ganhou", settings["emoteWon"])
		outputMessage = outputMessage.replace("$perdeu", settings["emoteLost"])
		outputMessage = outputMessage.replace("$moeda", Parent.GetCurrencyName())
		outputMessage = outputMessage.replace("$comando", settings["command"])

		Parent.SendStreamMessage(outputMessage)
	return

def ReloadSettings(jsonData):
	Init()
	return

def OpenReadMe():
	location = os.path.join(os.path.dirname(__file__), "LeiaMe.txt")
	os.startfile(location)
	return

def Tick():
	return

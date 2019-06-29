import subprocess
import helpers.config as config
import helpers.game as gconfig
import helpers.utils as utils

import helpers.creator as creator
import helpers.targeter as targeter
import helpers.puller as puller
import helpers.pusher as pusher
import helpers.signer as signer
import helpers.builder as builder
import helpers.shipper as shipper

from helpers.game import Game

import os

def printInfo():
	options = (
'''
COMMAND | DESCRIPTION                                                               | OPTIONAL PARAMS
________|___________________________________________________________________________|_________________
create  | Create a new fmc game                                                     | [game name]
target  | Targets a game, which will become the default for other commands          | [game name]
untarget| Removes a target                                                          |
unity   | Opens Unity project                                                       | [game name] all ask
status  | Check if any game has files to commit                                     | [game name]
pull    | Pull project and fmc subtree                                              | [game name] all
push    | Push the fmc framework from a project                                     | [game name]
build   | Build for Android and/or iOS                                              | [game name] all
sign    | Create a keystore to sign a project (for Android development)             | [game name] all
ship    | Inits fastlane, handle iOS certs and uploads to AppStore/PlayStore        | [game name] all android ios
test    | If a build exists, goes to testflight and updates the fmctesters group    | [game name] all
check   | If a build exists, checks the tester list on testflight                   | [game name] all
fill    | If a build exists, updates the app test information.                      | [game name] all

If you want, you can specify only the beginning of the name, fmc will try to complete!

 -- EXAMPLES --
create myawesomegame
target myawes           //fmc will autocomplete
pull
pull all
build all
build android
build ios all
unity all              //will open every game one after another
unity all ask          //will open every game one after another, asking for every game
ship
''')
	print(options)

def fmcInput():
	target = config.getTargetGame()
	if target is not None:
		message = f"fmc ({target.internalGameName})>"
	else:
		message = "fmc>"

	return input(message)

def reactToCommand(command):
	commandList = utils.parList(command)
	targetedGame = config.getTargetGame()
	games = config.getFMCGames()

	firstCommand = commandList[0];
	secondCommand = None
	if len(commandList) > 1:
		secondCommand = commandList[1];

	#Since platforms are useful for more commands, let's check them here
	targetAndroid = False
	targetIOS = False
	if "android" in commandList:
		targetAndroid = True
	if "ios" in commandList:
		targetIOS = True
	if not (targetAndroid or targetIOS):
		targetAndroid = True
		targetIOS = True

	if command == "info":
		printInfo()

	elif firstCommand == "create":
		gameName = ""
		if secondCommand is not None:
			gameName = secondCommand
		creator.createNewProject(gameName)

	elif firstCommand == "untarget":
		targeter.untarget()

	else: #if here, we are working on existing games		
		#trying to find the targeted game
		toTarget = targetedGame
		if secondCommand is not None:
			if secondCommand != "" and secondCommand != "all" and not Game.isValidGame(secondCommand):
				for g in games:
					if g.internalGameName.startswith(secondCommand) and utils.readYesNo("Did you mean " + g.internalGameName + "?", True):
						secondCommand = g.internalGameName
						break
			if Game.isValidGame(secondCommand):
				toTarget = Game.fromInternalName(secondCommand)

		if firstCommand == "target":
			if toTarget is not None:
				targeter.target(secondCommand)
			else:
				targeter.target(None)

		elif firstCommand == "unity":
			if "all" in commandList:
				Game.launchUnityForAllGames("ask" in commandList)
			else:
				if toTarget is None: toTarget = Game.pick(True, "All")
				if toTarget is None: Game.launchUnityForAllGames("ask" in commandList) #The user selected "All"
				else: toTarget.launchUnity(None, False)

		elif firstCommand == "status":
			if toTarget is not None and secondCommand != "all":
				toTarget.hasFilesToCommit(True,True)
			else:
				gamesWithFilesToCommit = Game.getGamesWithFilesToCommit(True,False)
				if len(gamesWithFilesToCommit) <= 0:
					print("CLEAN - All games have no files to commit!")

		elif firstCommand == "pull":
			if "all" in commandList:
				puller.pullAll()
			else:
				if toTarget is None: toTarget = Game.pick(True, "All")
				if toTarget is None: puller.pullAll() #The user selected "All"
				else: puller.pull(toTarget, True)

		elif firstCommand == "push":
			#By default uses targeted game. If overridden, use the given one  
			if toTarget is None: toTarget = Game.pick(False)
			pusher.push(toTarget) #if targeted game is None, a picker will appear

		elif firstCommand == "sign":
			if "all" in commandList:
				signer.signAll()
			else:
				if toTarget is None: toTarget = Game.pick(True, "All")
				if toTarget is None: signer.signall() #The user selected "All"
				else: signer.sign(toTarget)

		elif firstCommand == "build":
			if "all" in commandList:
				builder.buildAll(targetAndroid, targetIOS)
			else:
				if toTarget is None: toTarget = Game.pick(True, "All")
				if toTarget is None: builder.buildAll(targetAndroid, targetIOS) #The user selected "All"
				else: builder.build(toTarget, targetAndroid, targetIOS)

		elif firstCommand == "ship":
			if "all" in commandList:
				shipper.shipAll(targetAndroid, targetIOS)
			else:
				if toTarget is None: toTarget = Game.pick(True, "All")
				if toTarget is None: shipper.shipAll(targetAndroid, targetIOS) #The user selected "All"
				else: shipper.ship(toTarget, targetAndroid, targetIOS)

		elif firstCommand == "test":
			if "all" in commandList:
				shipper.updateAllIOSTesters()
			else:
				if toTarget is None: toTarget = Game.pick(True, "All")
				if toTarget is None: shipper.updateAllIOSTesters() #The user selected "All"
				else: shipper.updateIOSTesters(toTarget)
		
		elif firstCommand == "check":
			if "all" in commandList:
				shipper.checkAllIOS()
			else:
				if toTarget is None: toTarget = Game.pick(True, "All")
				if toTarget is None: shipper.checkAllIOS(targetAndroid, targetIOS) #The user selected "All"
				else: 
					shipper.checkIOS(toTarget)

		elif firstCommand == "fill":
			if "all" in commandList:
				shipper.fillAllIOSTestInfo()
			else:
				if toTarget is None: toTarget = Game.pick(True, "All")
				if toTarget is None: shipper.fillAllIOSTestInfo() #The user selected "All"
				else: 
					shipper.fillIOSTestInfo(toTarget)

		else:
			if command != "":
				print("invalid command. Use 'info' to get a list of available commands.")

def main():
	utils.printWhiteLines(1)
	utils.openPar("Welcome to the fmc toolkit. Type 'info' to get command list")
	waitingForCommand = True
	try:
		while True:
			try:
				waitingForCommand = True
				command = fmcInput()
				waitingForCommand = False
				reactToCommand(command)
			except KeyboardInterrupt:
				utils.printWhiteLines(1)
				if waitingForCommand: 
					input("Ctrl+C again to exit, enter to return to fmc")
	except KeyboardInterrupt:
		pass

#Let's execute the main function
main()
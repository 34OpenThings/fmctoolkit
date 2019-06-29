import subprocess
import helpers.config as config
import helpers.utils as utils
import os

def printInfo():
	gamesFolderPath = config.getFMCGamesFolderPath()
	numberOfGames = len(config.getFMCGames())
	utils.openPar("PROJECT BUILDER - this script will build " + str(numberOfGames) + " games" 
		+ "\nProjects path:  " + gamesFolderPath 
		+ "\nNOTE:this might take a long time!")
	utils.waitForEnterKey()

def buildOnPlatform(game, isAndroid):
	errorsOccured = False
	platformName = None
	methodName = None

	if isAndroid:
		platformName = 'android'
		methodName = config.unityAndroidBuildMethodName
		print("Building for Android...")
	else:
		platformName = 'ios'
		methodName = config.unityIOSBuildMethodName
		print("Building for iOS...")
	
	errorsOccured = game.runUnityMethod(methodName)

	return errorsOccured

def build(game, buildAndroid, buildIOS):
	incrementVersions(game)
	
	errorsOccured = False
	if buildAndroid:
		errorsOccured = errorsOccured or buildOnPlatform(game, True)
	if buildIOS:
		errorsOccured = errorsOccured or buildOnPlatform(game, False)

def incrementVersions(game):
	print("Incrementing versions and committing changes...")
	
	errorsOccured = game.runUnityMethod(config.unityIncrementVersionsMethodName)
	game.gitAdd("ProjectSettings/ProjectSettings.asset")
	game.gitCommit("New version")
	game.gitPush()
	
	return errorsOccured

def buildAll(buildAndroid, buildIOS):
	printInfo()
	games = config.getFMCGames()
	numberOfGames = len(games)

	errorsOccured = False
	gameNumber = 1
	for game in games:#for each project in the fmc folder
		utils.openPar ("(" + str(gameNumber) + "/" + str(numberOfGames) + ") BUILDING: " + game.gamePath)

		errorsOccured = errorsOccured or build(game, buildAndroid, buildIOS)

		gameNumber += 1
		utils.printWhiteLines(1);

	if errorsOccured:
		utils.closePar("COMPLETED WITH ERRORS")
	else:
		utils.closePar("FINISHED")



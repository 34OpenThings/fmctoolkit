import subprocess
import xml.etree.ElementTree
import helpers.config as config
import helpers.utils as utils
from helpers.game import Game

def printInfo():
	fmcRepoURL = config.getFMCRepoURL()
	gamesFolderPath = config.getFMCGamesFolderPath()
	numberOfGames = len(config.getFMCGames())

	utils.openPar("FRAMEWORK PULL - The script will pull the fmc subtree in " + str(numberOfGames) + " games" 
		+ "\nProjects path:  " + gamesFolderPath 
		+ "\nFramework repo: " + fmcRepoURL 
		+ "\nNOTE:The script is going to git reset hard every project!")

def pull(game, checkForCommits):
	if checkForCommits:
		hasFiles = game.hasFilesToCommit(True, False)
		if hasFiles and not utils.readYesNo("Do you want to proceed? " + game.internalGameName + " will be resetted!", True):
			return

	print("Pulling: " + game.gamePath)
	fmcRepoURL = config.getFMCRepoURL()

	game.gitAdd(".")
	game.gitResetHard()
	game.gitPull()
	game.gitSubtreePull()
	game.gitPush()

def pullAll():
	games = config.getFMCGames()
	numberOfGames = len(games)

	gamesWithFilesToCommit = Game.getGamesWithFilesToCommit(False,False)

	if len(gamesWithFilesToCommit) > 0:
		print("WARNING - the following games have files to commit! You can use 'status' to check them:")
		for g in gamesWithFilesToCommit:
			print(g.gamePath)

		if not utils.readYesNo("Do you want to proceed? All games will be resetted!", True):
			return

	gameNumber = 1
	for g in games:
		utils.openPar ("(" + str(gameNumber) + "/" + str(numberOfGames) + ") UPDATING: " + g.gamePath)
		pull(g, False)
		utils.closePar ("SUCCESSFULLY UPDATED: " + g.gamePath)
		utils.printWhiteLines(2)
		gameNumber += 1

	utils.closePar("FINISHED")

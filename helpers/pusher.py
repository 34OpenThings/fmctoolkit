import subprocess
import xml.etree.ElementTree
import helpers.config as config
import helpers.utils as utils
import helpers.puller as puller
import os
from helpers.game import Game

def printInfo():
	fmcRepoURL = config.getFMCRepoURL()
	utils.openPar("FRAMEWORK PUSH - The script will push the fmc subtree to the framework repo." 
		+ "\nFramework repo: " + fmcRepoURL 
		+ "\nNOTE:Commit before using! The script is going to git reset hard the selected game!")

def push(game):
	utils.closePar("Pushing from " + game.gamePath);

	game.gitResetHard()
	game.gitPull()
	game.gitSubtreePush()
	game.gitSubtreePull()
	game.gitPush()

	if utils.readYesNo("Do you want to pull the framework in every project?", True):
		puller.pullAll()
	else:
		utils.closePar("FINISHED")

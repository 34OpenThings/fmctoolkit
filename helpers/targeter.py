import subprocess
import helpers.config as config
import helpers.utils as utils
import os
from helpers.game import Game

def printInfo():
	utils.openPar("TARGETER - Select a project to make it the default of the toolkit actions!")

def target(internalGameName):
	if internalGameName is not None and not Game.isValidGame(internalGameName):
		print("Game name is invalid! Select another.")
		internalGameName = None

	if internalGameName is None:
		game = Game.pick(True)
		if game is None:
			untarget()
		else:
			config.setTargetGame(game.gamePath)
	else: #a valid name was inserted
		config.setTargetGame(Game.fromInternalName(internalGameName).gamePath)

def untarget():
	config.setTargetGame("")

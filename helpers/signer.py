import subprocess
import helpers.config as config
import helpers.utils as utils
import os
from helpers.game import Game

def printInfo():
	games = config.getFMCGames()
	numberOfGames = len(games)
	utils.openPar("ANDROID SIGNER - The script, if needed, will create a keystore file in " + str(numberOfGames) + " games" + "\nProjects path:  " + gamesFolderPath)

def sign(game):

	#These fields must not contain spaces! If you need them, modify utils.parList.
	password = config.getKeystorePassword()
	companyName = config.getCompanyName()
	keystoreName = "fmc.keystore"
	alias = "fmc"

	keystorePath = os.path.join(game.gamePath, keystoreName)
	if os.path.isfile(keystorePath):
		print("SKIPPING: A keystore already exist in: " + keystorePath)
	else:
		print("OK, SIGNING: ", game.gamePath)
		pars = (f'keytool -genkey -v -keystore {keystoreName} -sigalg SHA1withRSA -alias {alias} ' +
				f'-keyalg RSA -keysize 2048 -validity 30000 -keypass {password} ' +
				f'-storepass {password} -dname O={companyName}')
		subprocess.call(utils.parList(pars), cwd=game.gamePath)

		game.gitPull()
		game.gitAdd(keystoreName)
		game.gitCommit("Added keystore file")
		game.gitPush()
	utils.printWhiteLines(1)

def signAll():
	games = config.getFMCGames()
	numberOfGames = len(games)
	gameNumber = 1
	for g in games:#for each game in the fmc folder
		sign(g)
import helpers.config as config
import helpers.utils as utils
import helpers.game as game
import subprocess
import shutil
import sys
import time
import os
import webbrowser
from helpers.game import Game

def printIntro():
	utils.openPar('''PROJECT CREATOR - this script initializes a new fmc game:
	- Creates a new Unity project inside the fmc games folder
	- Inits a git repo with a Unity .gitignore
	- Creates a git remote repo
	- Pulls the fmc framework subtree and creates the _content folder
	- Pushes everything
	''')

def isGameNameValid(gamePath, gameName):
	ok = False
	if gameName != '' and not(' ' in gameName):
		ok = True;

	if ok and os.path.exists(gamePath):
		print(gamePath,' already exists.')
		ok = False;
	return ok

def createNewProject(gameName):
	unityExePath = config.getUnityExePath();
	unityExeFolderPath = os.path.abspath(os.path.join(unityExePath, os.pardir))
	gamesFolderPath = config.getFMCGamesFolderPath()
	parentRemoteURL = config.getParentRemoteURL()
	fmcRepoURL = config.getFMCRepoURL()

	#asking for project name
	gamePath = os.path.join(gamesFolderPath, gameName)
	ok = isGameNameValid(gamePath, gameName)
	if not ok:
		printIntro()
		while not ok:
			gameName = input('Enter the internal game name (no spaces, all lowercase! - e.g. stopthefall): ')
			gamePath = os.path.join(gamesFolderPath, gameName)
			ok = isGameNameValid(gamePath, gameName)

	repoUrl = parentRemoteURL + gameName

	#we have a valid game path and git repo. Ask for confirm...
	utils.printWhiteLines(2);
	utils.openPar(
		  "\nProject root: " + gamePath 
		+ "\nRemote repo:  " + repoUrl 
		+ "\nInternal name:" + gameName);
	utils.waitForEnterKey()

	#creating Unity project...
	print('Creating Unity project. This will take some time...')
	pars = [unityExePath] + utils.parList('-quit -batchmode -nographics -createproject') + [gamePath]
	subprocess.call(pars)
	print('Unity project created!')
	time.sleep(1)

	game = Game(gamePath)

	#init local git repo...
	subprocess.call(utils.parList("git init"), cwd=gamePath)
	subprocess.call(utils.parList("git remote add origin", repoUrl), cwd=gamePath)

	#adding .gitignore...
	shutil.copy(config.unityGitignorePath, os.path.join(gamePath, ".gitignore"))
	game.gitAdd(".gitignore")
	game.gitCommit("Added .gitignore")

	#creating remote repo...
	remoteURL = parentRemoteURL + gameName + ".git";
	subprocess.call(utils.parList("git push --set-upstream", remoteURL, "master"), cwd=gamePath)

	#first commit...
	game.gitAdd(".")
	game.gitCommit("Initial commit")

	#adding subtree...
	subprocess.call(utils.parList("git pull -u origin master"), cwd=gamePath)
	subprocess.call(utils.parList("git subtree add --prefix", config.gitSubtreePrefix, fmcRepoURL, "master --squash"), cwd=gamePath)
	subprocess.call(utils.parList("git push -u origin master"), cwd=gamePath)

	#creating _content folders...
	utils.createFolder(os.path.join(gamePath, config.fmcContentFolder))
	utils.createFolder(os.path.join(gamePath, config.fmcContentFolder, "Images"))
	utils.createFolder(os.path.join(gamePath, config.fmcContentFolder, "Prefabs"))
	utils.createFolder(os.path.join(gamePath, config.fmcContentFolder, "Scripts"))

	#Launching project and creating game settings
	print("Opening the game and creating settings...")
	game.runUnityMethod(config.unityUpdateSettingsMethodName)
	game.gitAdd(".")
	game.gitCommit("Added game settings")
	game.gitPush()

	webbrowser.open(remoteURL)
	os.startfile(os.path.realpath(gamePath))

	game.launchUnity(config.unityFirstProjectLaunchMethodName, False)

	utils.closePar("FINISHED")
import subprocess
import helpers.config as config
import helpers.game as gconfig
import helpers.utils as utils
import shutil
import platform
import os

def initFastlane(game):
	gameCfg = game.getConfig()

	#Creating fastlane folder
	fastlanePath = os.path.join(game.getIOSBuildPath(), "fastlane")
	if not os.path.exists(fastlanePath):
		os.makedirs(fastlanePath)

	#Creating Fastfile
	fastFile = config.getFastlaneFastFile()

	fastFile = fastFile.replace("$BUNDLE_ID$", gameCfg.bundleId)
	fastFile = fastFile.replace("$GAME_TITLE$", gameCfg.gameTitle)
	fastFile = fastFile.replace("$APPLE_ID_EMAIL$", config.getAppStoreMail())
	fastFile = fastFile.replace("$FASTLANE_CERTS_REPO_MAIL$", config.getFastlaneCertsRepoMail())
	fastFile = fastFile.replace("$FASTLANE_CERTS_REPO_URL$", config.getFastlaneCertsRepoURL())
	
	fastFile = fastFile.replace("$TESTERS_FEEDBACK_EMAIL$", config.getTestersFeedbackEmail())
	fastFile = fastFile.replace("$TESTERS_CONTACT_EMAIL$", config.getTestersContactEmail())
	fastFile = fastFile.replace("$TESTERS_CONTACT_FIRST_NAME$", config.getTestersContactFirstName())
	fastFile = fastFile.replace("$TESTERS_CONTACT_LAST_NAME$", config.getTestersContactLastName())
	fastFile = fastFile.replace("$TESTERS_CONTACT_PHONE$", config.getTestersContactPhone())
	fastFile = fastFile.replace("$TESTERS_TEST_NOTES$", config.getTestersTestNotes())

	fastFile = fastFile.replace("$APPSTORE_CONNECT_TEAM_ID$", config.getFastlaneAppStoreConnectTeamId())
	fastFile = fastFile.replace("$TEST_GROUP_NAME$", config.getTestGroupName())
	fastFile = fastFile.replace("$DEV_PORTAL_TEAM_ID$", config.getFastlaneDevPortalTeamId())

	fastFile = fastFile.replace("$PLAY_CONSOLE_JSON_KEY$", config.getPlayConsoleJSONKey())
	fastFile = fastFile.replace("$GAME_INTERNAL_NAME$", game.internalGameName)

	with open(os.path.join(fastlanePath, "Fastfile"), "w") as f:
		f.write(fastFile)
		f.close()

	print("Fastfile created!")

def setLocaleToUTF8(): #fastlane requires this to work properly
	os.environ["LC_ALL"] = "en_US.UTF-8"
	os.environ["LANG"] = "en_US.UTF-8"

def updateIOSTesters(game):
	#for these commands, I currently cannot use a lane, because they are sub actions.
	print("Distributing build to testers: " + str(config.getTestersMails()))
	gameCgf = game.getConfig()
	subprocess.call(utils.parList(f"fastlane pilot add -u {config.getAppStoreMail()} -a {gameCgf.bundleId} -g fmctesters") + config.getTestersMails(), cwd=game.gamePath)
	subprocess.call(utils.parList(f"fastlane pilot distribute --username {config.getAppStoreMail()} --app_identifier {gameCgf.bundleId} -g fmctesters --distribute_external true"), cwd=game.gamePath) 

def shipIOS(game):
	buildPath = game.getIOSBuildPath()
	setLocaleToUTF8();
	subprocess.call(utils.parList("fastlane fmcproduce"), cwd=buildPath)
	subprocess.call(utils.parList("fastlane fmcmatch"), cwd=buildPath)
	subprocess.call(utils.parList("fastlane fmctestflight"), cwd=buildPath)
	subprocess.call(utils.parList("fastlane fmcsettestinfo"), cwd=buildPath)
	subprocess.call(utils.parList("fastlane fmccreatetestgroup"), cwd=buildPath)
	updateIOSTesters(game)

def shipAndroid(buildPath):
	setLocaleToUTF8();
	subprocess.call(utils.parList("fastlane fmcsupply"), cwd=buildPath)

def printInfo():
	gamesFolderPath = config.getFMCGamesFolderPath()
	games = config.getFMCGames()
	numberOfGames = len(games)
	utils.openPar("SHIPPER - The script will ship via fastlane in " + str(numberOfGames) + " games" + "\nProjects path:  " + gamesFolderPath)

def ship(game, shipOnAndroid, shipOnIOS):
	if platform.system() != "Darwin":
		print("You can only ship on Macs. The shipper uses fastlane!")
		return

	gameBuildPath = game.getBuildFolderPath()

	if os.path.isdir(gameBuildPath):
		print("Found build folder", gameBuildPath);
		
		iOSBuildPath = game.getIOSBuildPath()
		if shipOnIOS:
			if os.path.isdir(iOSBuildPath):
				initFastlane(game)
				print("OK, SHIPPING: ", iOSBuildPath)
				shipIOS(game)
			else:
				print("ERROR: iOS build not found: ", iOSBuildPath)

		if shipOnAndroid:
			androidBuildPath = game.getAndroidBuildPath()
			if os.path.isfile(androidBuildPath):
				print("OK, SHIPPING: ", androidBuildPath)
				shipAndroid(iOSBuildPath) #fastlane is in the iOS build folder
			else:
				print("ERROR: Android build not found: ", androidBuildPath)
	else:
		print("Path not found: ", gameBuildPath);

def shipAll(shipOnAndroid, shipOnIOS):
	games = config.getFMCGames()
	numberOfGames = len(games)
	gameNumber = 1
	for game in games:#for each game in the fmc folder
		utils.openPar ("(" + str(gameNumber) + "/" + str(numberOfGames) + ") SHIPPING: " + game.gamePath)
		ship(game, shipOnAndroid, shipOnIOS)
		gameNumber += 1
		utils.printWhiteLines(2)

def updateAllIOSTesters():
	games = config.getFMCGames()
	numberOfGames = len(games)
	gameNumber = 1
	for game in games:#for each game in the fmc folder
		utils.openPar ("(" + str(gameNumber) + "/" + str(numberOfGames) + ") UPDATING TESTERS: " + game.gamePath)
		updateIOSTesters(game, shipOnAndroid, shipOnIOS)
		gameNumber += 1
		utils.printWhiteLines(2)

def checkIOSTesters(game):
	gameCgf = game.getConfig()
	if gameCgf is None:
		print(game.internalGameName + " was not built on this machine. Unable to get config.")
	else:
		subprocess.call(utils.parList(f"fastlane pilot list -u {config.getAppStoreMail()} -a {gameCgf.bundleId}"), cwd=game.gamePath)

def checkIOSBuilds(game):
	gameCgf = game.getConfig()
	if gameCgf is None:
		print(game.internalGameName + " was not built on this machine. Unable to get config.")
	else:
		subprocess.call(utils.parList(f"fastlane pilot builds -u {config.getAppStoreMail()} -a {gameCgf.bundleId}"), cwd=game.gamePath)

def checkIOS(game):
	gameCgf = game.getConfig()
	if gameCgf is None:
		print(game.internalGameName + " was not built on this machine. Unable to get config.")
	else:
		checkIOSBuilds(game)
		checkIOSTesters(game)

def checkAllIOS():
	games = config.getFMCGames()
	numberOfGames = len(games)
	gameNumber = 1
	for game in games:#for each game in the fmc folder
		utils.openPar ("(" + str(gameNumber) + "/" + str(numberOfGames) + ") CHECKING APP STORE FOR: " + game.gamePath)
		checkIOS(game)
		gameNumber += 1
		utils.printWhiteLines(2)

def fillIOSTestInfo(game):
	gameBuildPath = game.getBuildFolderPath()

	if os.path.isdir(gameBuildPath):
		print("Found build folder", gameBuildPath);
		
		iOSBuildPath = game.getIOSBuildPath()
		if os.path.isdir(iOSBuildPath):
			initFastlane(game)
			subprocess.call(utils.parList("fastlane fmcfilltestinfo"), cwd=iOSBuildPath)

def fillAllIOSTestInfo():
	games = config.getFMCGames()
	numberOfGames = len(games)
	gameNumber = 1
	for game in games:#for each game in the fmc folder
		utils.openPar ("(" + str(gameNumber) + "/" + str(numberOfGames) + ") FILLING TESTFLIGHT TEST INFO FOR : " + game.gamePath)
		fillIOSTestInfo(game)
		gameNumber += 1
		utils.printWhiteLines(2)	

import xml.etree.ElementTree
import os
import helpers.config as config
import helpers.utils as utils
import subprocess

class Game:
	def __init__(self, path):
		self.gamePath = path.strip()
		self.internalGameName = utils.getFolderNameFromPath(path)

	def gitResetHard(self):
		subprocess.call(utils.parList("git reset --hard"), cwd=self.gamePath)

	def gitAdd(self, filePath):
		subprocess.call(utils.parList("git add " + filePath), cwd=self.gamePath)

	def gitCommit(self, message):
		subprocess.call(utils.parList('git commit -m') + [message], cwd=self.gamePath)

	def gitPull(self):
		subprocess.call(utils.parList("git pull"), cwd=self.gamePath)

	def hasFilesToCommit(self, showWhich, showNothingToCommitMessage):
		statusOutput = subprocess.check_output(utils.parList("git status -s"), cwd=self.gamePath)
		out = statusOutput.decode('ascii').strip();
		hasFiles = len(out) > 0;
		if showWhich:
			if hasFiles:
				print(self.internalGameName + ":")
				out = "\n".join(("    ") + i.strip() for i in out.splitlines())
				print(out)
			elif showNothingToCommitMessage:
				print(self.internalGameName + " has nothing to commit")

		return hasFiles;

	def gitPush(self):
		subprocess.call(utils.parList("git push"), cwd=self.gamePath)

	def gitSubtreePull(self):
		subprocess.call(utils.parList("git subtree pull --prefix", config.gitSubtreePrefix, config.getFMCRepoURL(), "master --squash"), cwd=self.gamePath)

	def gitSubtreePush(self):
		subprocess.call(utils.parList("git subtree push --prefix", config.gitSubtreePrefix, config.getFMCRepoURL(), "master"), cwd=self.gamePath)

	def getConfig(self):
		fmcInfoFileName = "fmcinfo.xml"
		fmcinfopath = os.path.join(config.getFMCGamesFolderPath(), self.internalGameName, config.unityBuildFolderName, fmcInfoFileName)
		
		if os.path.isfile(fmcinfopath):
			return GameConfig(fmcinfopath)
		else:
			return None

	def getBuildFolderPath(self):
		return os.path.join(self.gamePath, config.unityBuildFolderName)
		
	def getAndroidBuildPath(self):
		return os.path.join(self.getBuildFolderPath(), self.internalGameName + ".apk")
		
	def getIOSBuildPath(self):
		return os.path.join(self.getBuildFolderPath(), self.internalGameName + "_xcode") #the _xcode should be also hardcoded in the builder of the toolkit

	def runUnityMethod(self, methodName):
		unityExePath = config.getUnityExePath()

		try:
			pars = [unityExePath] + utils.parList('-quit -batchmode -executeMethod', methodName) + ['-projectPath', self.gamePath]
			subprocess.check_call(pars)
			print("SUCCESS")
		except subprocess.CalledProcessError: # handle errors in the called executable
			print("FAILED")
			errorsOccured = True
		except OSError: # executable not found
			errorsOccured = True

	def launchUnity(self, methodName, waitForExit):
		print("Launching " + self.internalGameName + "...")
		unityExePath = config.getUnityExePath()
		try:
			method = utils.parList('-executeMethod', methodName) if methodName is not None else []
			pars = [unityExePath] + method + ['-projectPath', self.gamePath]
			if waitForExit:
				subprocess.check_call(pars)
			else:
				subprocess.Popen(pars)
			print("SUCCESS")
		except subprocess.CalledProcessError: # handle errors in the called executable
			print("FAILED")
			errorsOccured = True
		except OSError: # executable not found
			errorsOccured = True

	@staticmethod
	def fromInternalName(internalGameName):
		path = os.path.join(config.getFMCGamesFolderPath(), internalGameName)
		return Game(path) if os.path.isdir(path) else None

	@staticmethod
	def isValidGame(internalGameName):
		return internalGameName is not None and internalGameName != "" and Game.fromInternalName(internalGameName) != None

	@staticmethod
	def pick(allowNone, noneMessage = "None"):
		games = config.getFMCGames()
		game = None

		if allowNone:
			print(f"0 - [{noneMessage}]")
		i = 1;
		for g in games:
			print(str(i) + " - " + g.internalGameName)
			i += 1

		utils.printWhiteLines(1)
		projectNumber = -1
		min = 0 if allowNone else 1
		while projectNumber < min or projectNumber > i-1:
			projectNumber = utils.readIntInRange("Insert the project number:", min, i-1)
			if projectNumber > 0:
				game = games[projectNumber-1]

		return game

	@staticmethod
	def getGamesWithFilesToCommit(showWhich, showNothingToCommitMessage):
		games = []
		utils.printWhiteLines(1)
		for g in config.getFMCGames():
			hasFiles = g.hasFilesToCommit(showWhich, showNothingToCommitMessage)
			if hasFiles:
				games.append(g);
				if showWhich:
					utils.printWhiteLines(1)
		return games

	@staticmethod
	def launchUnityForAllGames(askForEachProject):
		if not utils.readYesNo("The script will launch the next game when you close the previous. Continue?", True):
			return

		for g in config.getFMCGames():
			if not askForEachProject or utils.readYesNo("Open " + g.internalGameName + "?", True):
				g.launchUnity(None, True)

class GameConfig:
	def __init__(self, fmcinfopath):
		e = xml.etree.ElementTree.parse(fmcinfopath).getroot()

		self.gameTitle = e.find("gametitle").text
		self.bundleId = e.find("bundleid").text
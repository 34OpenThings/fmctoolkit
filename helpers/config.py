import xml.etree.ElementTree
import os
from helpers.game import Game

#####################################
## resources files path

configFileName = "resources/config.xml"
unityGitignorePath = "resources/unity.gitignore"#path of the templated gitignore
fastlaneFastFilePath = "resources/fastfile"

#####################################
## hard-coded stuff

gitSubtreePrefix = "Assets/_fmc" #path in which the framework is located, relative to the root of the fmc game
fmcContentFolder = "Assets/_content"#path in which the user will work
unityAndroidBuildMethodName = "FMCBuilder.BuildAndroid"
unityIOSBuildMethodName = "FMCBuilder.BuildIOS"
unityIncrementVersionsMethodName = "FMCBuilder.IncrementVersions"
unityUpdateSettingsMethodName = "FMCGameSettingsWindow.UpdateUnitySettingsFromToolkit"
unityFirstProjectLaunchMethodName = "FMCGameSettingsWindow.FirstProjectLaunch"

unityBuildFolderName = "_fmcbuilds"#folder containing the builds, relative to the project root

#####################################
## FMC

def getFMCGames():
	parentFolder = getFMCGamesFolderPath()
	return [Game(os.path.join(parentFolder,x)) for x in os.listdir(parentFolder) if os.path.isdir(os.path.join(parentFolder, x))]

def getFMCGamesFolderPath():
	return getSingleParameter('gamesfolder')

def getNGUIFolderPath():
	return getSingleParameter('nguifolder')

def getUnityExePath():
	return getSingleParameter('unityexepath')

def getFMCRepoURL():
	return getSingleParameter('fmcrepourl')

def getCompanyName():
	return getSingleParameter('companyname')

def getKeystorePassword():
	return getSingleParameter('keystorepassword')

def getParentRemoteURL():
	url = getSingleParameter('fmcparentremoteurl')
	if not str.endswith(url, "/"):
		url = url + "/"
	return url

def getTargetGame():
	target = getSingleParameter('targetgame')
	if target is not None and target != "":
		return Game(target)
	else:
		return None

def setTargetGame(gameName):
	SetSingleParameter('targetgame', gameName)

def getTestGroupName():
	return getSingleParameter('testgroupname')

def getTestersMails():
	return getSingleParameter('testersmails').split(",")

def getAppStoreMail():
	return getSingleParameter('appstoremail')

def getTestersFeedbackEmail():
	return getSingleParameter('testersfeedbackemail')

def getTestersContactEmail():
	return getSingleParameter('testerscontactemail')

def getTestersContactFirstName():
	return getSingleParameter('testerscontactfirstname')

def getTestersContactLastName():
	return getSingleParameter('testerscontactlastname')

def getTestersContactPhone():
	return getSingleParameter('testerscontactphone')

def getTestersTestNotes():
	return getSingleParameter('testerstestnotes')

#####################################
## Fastlane

def getFastlaneFastFile():
	return open(fastlaneFastFilePath, 'r').read()

def getFastlaneAppStoreConnectTeamId():
	return getSingleParameter('fastlaneappstoreconnectteamid')
	
def getFastlaneDevPortalTeamId():
	return getSingleParameter('fastlanedevportalteamid')

def getPlayConsoleJSONKey():
	return getSingleParameter('playconsolejsonkey')

def getFastlaneCertsRepoURL():
	return getSingleParameter('fastlanecertsrepourl')

def getFastlaneCertsRepoMail():
	return getSingleParameter('fastlanecertsrepomail')

#####################################
## Utils

def getSingleParameter(parameterName):
	e = xml.etree.ElementTree.parse(configFileName).getroot()
	return e.find(parameterName).text

def SetSingleParameter(parameterName, parameterValue):
	e = xml.etree.ElementTree.parse(configFileName)
	e.find(parameterName).text = parameterValue
	e.write(configFileName)


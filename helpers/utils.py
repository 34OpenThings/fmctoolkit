import os
import helpers.config as config
import subprocess

def printWhiteLines(n):
	for x in range(0, n):
		print("")

def printSeparator():
	print("********************************************************************")

def openPar(text):
	printSeparator()

	for l in text.split('\n'):
		l.strip()
		if(l != ""):
			print("*********** " + l)

	printSeparator()
	print("")

def closePar(text):
	for l in text.split('\n'):
		l.strip()
		if(l != ""):
			print("-- " + l + " --")

def waitForEnterKey():
	print("\nPress Enter to continue ...")
	input()

#Splits a list of strings into a list of parameters. ["git commit -m", "initial commit"] becomes ["git", "commit", "-m", "initial commit"]
def parList(*sl):
	final = []
	for s in sl:
		s.strip();
		final += s.split(" ")
	return final

def createFolder(directory):
	try:
	    if not os.path.exists(directory):
	        os.makedirs(directory)
	except OSError:
	    print ('Error: Creating directory. ' +  directory)

def getFolderNameFromPath(path):
	if str.endswith(path, "/"):
		path = path[:-1]
	return os.path.basename(path)

def _yesno(message, hasDefault, default):
	defaultAnswer = "Yes" if default else "No" 
	booleanAnswer = default
	message += " (y/n)"
	message += " - default is " + defaultAnswer + ": " if hasDefault else ":"

	isValidAnswer = False
	while(not isValidAnswer):
		verbalAnswer = input(message)
		verbalAnswer = verbalAnswer.lower()

		if verbalAnswer == "y":
			isValidAnswer = True
			booleanAnswer = True
		if verbalAnswer == "n":
			isValidAnswer = True
			booleanAnswer = False
		if hasDefault and verbalAnswer == "":
			isValidAnswer = True #leaving default value of answer
	
	return booleanAnswer

def readYesNo(message, default):
	return _yesno(message, True, default)

def readYesNoWithoutDefault(message):
	return _yesno(message, False, False)

def stringIsInteger(s):
    if len(s) > 0 and s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

def readIntInRange(message, min, max):
	isValidAnswer = False
	message += " (" + str(min) + " to " + str(max) + ") :"
	numberPicked = 0

	while not isValidAnswer:
		verbalAnswer = input(message)
		if stringIsInteger(verbalAnswer):
			numberPicked = int(verbalAnswer)
			if min <= numberPicked and numberPicked <= max:
				isValidAnswer = True

	return numberPicked


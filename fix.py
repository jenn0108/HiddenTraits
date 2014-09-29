import sys
import os
import re

#python fix.py events "(trait = [a-z_]*)" "\1_hidden" "create[a-z_]*" 0

constPathName = "C:\\Users\\Jenn\\Documents\\Paradox Interactive\\Crusader Kings II\\mod\\HiddenTraits\\"

def processFile(infileFullPath, matchRegEx, replaceRegEx, scopeRegEx, isIn):
	newFile = open(infileFullPath + ".new", "w")
	file = open(infileFullPath)
	scopes = [(isIn == "0")]
	#print("Scope is:" + scopeRegEx)
	for line in file:
		if (re.match("(\s)*#",line)):
			newFile.write(line)
			continue
		match = re.match("(\t*[a-zA-Z0-9_]+) *= *\{(.*)\}(.*)", line)
		if (match):
			#print("Special case");
			# SKIP for now process match
			if (scopes[-1]):
				#print("Replacing:" + scopes[-1]);
				if(replaceRegEx.find("\\n") > -1 and re.search(matchRegEx, match.group(2))):
					tabsMatch = re.match("(\t*)",line)
					tabs = ""
					if (tabsMatch):
						tabs = tabsMatch.group(1)
					newFile.write(match.group(1) + " = {" + match.group(3) + "\n\t" + tabs + re.sub(matchRegEx,replaceRegEx.replace("\\n","\\n\t" + tabs), match.group(2)) + "\n" + tabs + "}\n")
				else:
					newFile.write(match.group(1) + " = {" + re.sub(matchRegEx,replaceRegEx, match.group(2)) + "}" + match.group(3) + "\n")
			else:
				newFile.write(line)
			continue
		match = re.search("([a-zA-Z0-9_]+) *= *\{", line)
		if (match):
			if(re.search(scopeRegEx, match.group(1))):
				#print("Match scope:" + match.group(1))
				scopes.append( (isIn == "1") )
			else:
				#print("No match: " + ("True" if scopes[-1] else "False"))
				scopes.append(scopes[-1])
			#print(match.group(1) + ": " + ("True" if scopes[-1] else "False"))
			newFile.write(line)
			continue
		if (re.search("\}", line)):
			#print("Popping");
			scopes.pop()
			newFile.write(line)
			continue
		if (scopes[-1]):
			#print("Replacing:" + line);
			tabsMatch = re.match("(\t*)",line)
			tabs = ""
			if (tabsMatch):
				tabs = tabsMatch.group(1)
			#Prefix the \n in the replaceRegEx with the appropriate
			#number of tabs.
			newFile.write(re.sub(matchRegEx,replaceRegEx.replace("\\n","\\n" + tabs),line))
		else:
			newFile.write(line)
	newFile.close()
	file.close()
	os.remove(infileFullPath)
	os.rename(infileFullPath + ".new", infileFullPath)
	


def doChanges(folderName, matchRegEx, replaceRegEx, scopeRegEx, isIn):
	for infile in os.listdir(os.path.join(constPathName, folderName)):
		processFile(os.path.join(constPathName, folderName, infile), matchRegEx, replaceRegEx, scopeRegEx, isIn)
		
if(len(sys.argv) < 5):
	print("Usage: python fix.py subdir search_exp replace_exp scope_exp isIn")
	print("\tsearch_exp and replace_exp are linked regular expressions")
	print("\tscope_exp is a regexp that defines which scopes are included")
	print("\tisIn determines whether scope_exp includes scopes or excludes them")
	exit()
		
doChanges(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
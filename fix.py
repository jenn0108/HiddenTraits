import sys
import os
import re

#python fix.py events "(trait = [a-z_]*)" "\1_hidden" "create[a-z_]*" 0

# Operate under the assumption that we are running from the root of the mod directory.
constPathName = ".\\"

def getPrefixTabs(line):
	tabsMatch = re.match("(\t*)",line)
	tabs = ""
	if (tabsMatch):
		tabs = tabsMatch.group(1)
		
	return tabs

def processFile(infileFullPath, matchRegEx, replaceRegEx, scopeRegEx, isIn):
	# Open the new file which we are going to write out to.  We will delete
	# the original file and rename the new one.
	newFile = open(infileFullPath + ".new", "w")
	file = open(infileFullPath)
	
	# Keep track of whether or not the current scope is in.  At each new scope
	# we determine whether or not we should perform the replacements in it. If
	# are including based on the scope, then we are implicitly ignoring scopes
	# above the matching ones.  This means that we start off excluding.  The
	# opposite happens if we are excluding based on the scope regex.  We don't*
	# need to remember scopes when we pop the stack, we only need to know whether
	# or not each scope was in/out.
	scopes = [(isIn == "0")]
	
	# We'll perform our logic for each line in the file, tracking scope in/out
	# as we go.  There are three major cases we need to consider:
	# 1. Lines that open and close a scope like "NOT = { trait = cruel }"
	#    where we need to perform our logic inside the scope and immediately end it.
	# 2. Lines that open a new scope like "trigger = {" where we need to determine
	#    whether or not the scope should have substitutions in it, but nothing else.
	# 3. Lines that close the current scope like "}"
	for line in file:
		# First off, ignore any lines that start with a comment.
		if (re.match("(\s)*#",line)):
			newFile.write(line)
			continue
			
		# Look for lines that open a scope and immediately close it. (Case #1)
		match = re.match("(\t*[a-zA-Z0-9_]+) *= *\{(.*)\}(.*)", line)
		if (match):
			if (scopes[-1]):
				# We're processing this scope so see if we need to replace anything.
				# There is a special case here.  Since we may be replacing a single line with multiple
				# lines (if the replacement has a newline).
				if(replaceRegEx.find("\\n") > -1 and re.search(matchRegEx, match.group(2))):
					# We're doing a replacement and it has a newline in it.  We'll replace each newline with an appropriate
					# number of tabs in order to preserve the look of the file.  We're also going to be changing the structure
					# so that the scope opens on the first line, and the close happen on the last.
					tabs = getPrefixTabs(line)
					
					# Update the replacement so that each newline has an appropriate number of tabs.  We add an extra one
					# since the lines after the opener should be indented.  We can't use re.sub here because it doesn't match
					# newlines correctly.
					updatedReplaceRegEx = replaceRegEx.replace("\\n","\\n\t" + tabs);
					
					newFile.write(match.group(1) + " = {" + match.group(3) + "\n\t" + tabs + re.sub(matchRegEx, updatedReplaceRegEx, match.group(2)) + "\n" + tabs + "}\n")
				else:
					# We're either not performing any replacement or it is simple and doesn't change the number of lines.
					newFile.write(match.group(1) + " = {" + re.sub(matchRegEx,replaceRegEx, match.group(2)) + "}" + match.group(3) + "\n")
			else:
				# We're ignoring this scope, just write out the line unchanged.
				newFile.write(line)
			continue
			
		# Look for lines that open a scope. (Case #2)
		match = re.search("([a-zA-Z0-9_]+) *= *\{", line)
		if (match):
			# Decide whether or not the current scope matches the scope regex.
			if(re.search(scopeRegEx, match.group(1))):
				# We match.  This means that we are in if we are supposed to be and out otherwise.
				scopes.append( (isIn == "1") )
			else:
				# We don't match.  This means that we aren't changing whether or not the current scope
				# is in or out.
				scopes.append(scopes[-1])
			newFile.write(line)
			continue
			
		# Look for lines that close a scope. (Case #3)
		if (re.search("\}", line)):
			scopes.pop()
			newFile.write(line)
			continue
			
		# Fall through.  Do the replacement if the lines match.
		if (scopes[-1]):
			tabs = getPrefixTabs(line)
			#Prefix the \n in the replaceRegEx with the appropriate
			#number of tabs.
			newFile.write(re.sub(matchRegEx,replaceRegEx.replace("\\n","\\n" + tabs),line))
		else:
			newFile.write(line)
	
	# Close the files.
	newFile.close()
	file.close()
	# Remove the original, and rename on the original to the original.
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
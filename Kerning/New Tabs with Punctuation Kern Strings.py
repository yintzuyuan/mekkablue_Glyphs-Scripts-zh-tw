#MenuTitle: New Tabs with Punctuation Kern Strings
# -*- coding: utf-8 -*-
__doc__="""
Outputs a kerning string with letters, figures, and punctuation.
"""

# ingredients:
thisFont = Glyphs.font
mID = thisFont.selectedFontMaster.id
Glyphs.defaults["visibleReporters"] = None

alwaysExclude = [".punch",".game","tic","youlose","p1win","p2win","RAINER", ".draw", ".win"]

def nameNotExcluded( suffix, exclusions ):
	for excludedString in exclusions:
		if excludedString in suffix:
			return False
	return True

uppercase = [g.name for g in thisFont.glyphs if g.export and g.subCategory=="Uppercase" and len(g.layers[mID].paths)>0 and g.script=="latin" and nameNotExcluded(g.name,alwaysExclude) ]
lowercase = [g.name for g in thisFont.glyphs if g.export and g.subCategory=="Lowercase" and len(g.layers[mID].paths)>0 and g.script=="latin" and nameNotExcluded(g.name,alwaysExclude) ]
smallcaps = [g.name for g in thisFont.glyphs if g.export and g.category == "Letter" and g.subCategory=="Smallcaps" and len(g.layers[mID].paths)>0 and g.script=="latin"  and nameNotExcluded(g.name,alwaysExclude) ]
fig = [g.name for g in thisFont.glyphs if g.export and g.subCategory=="Decimal Digit" and not ".tf" in g.name and not ".tosf" in g.name and nameNotExcluded(g.name,alwaysExclude)]

# clean up lowercase list:
fixDict = {"idotless":"i", "jdotless":"j"}
for searchName in fixDict:
	replaceName = fixDict[searchName]
	if not replaceName in lowercase and searchName in lowercase:
		index = lowercase.index(searchName)
		lowercase[index] = replaceName
	

# punctuation:
pairsOrSingles = [
	u"¿?", u"¡!", 
	".", ",", ":", ";", u"…",
	"()", "[]", "{}", 
	u"„“", u"‚‘", u"“”", u"‘’", 
	u"«»", u"»«", u"‹›", u"›‹", 
	u"-", u"–", u"—", u"@",
	u"*", "'", '"', u"•", u"|", u"¦"
]

# finish up punctuation:
controlString = "".join(pairsOrSingles)
for thisPunctuation in [g.charString() for g in thisFont.glyphs if g.export and (not g.charString() in controlString) and g.category=="Punctuation" and nameNotExcluded(g.name,alwaysExclude) ]:
	pairsOrSingles.append(thisPunctuation)

# kern strings:
lower = u""
upper = u""
number = u""

def pairAddition( i, pair, glyphname, linelength=10 ):
	if i%(linelength) == (linelength-1):
		whitespace = "\\n"
	else:
		whitespace = " "
	return "%s/%s %s%s" % ( pair[0], glyphname, pair[1], whitespace )

def singleAddition( i, single, glyphname, linelength=10 ):
	single = single.replace("/","/slash ").replace("\\","/backslash ")
	if i%(linelength) == (linelength-1):
		whitespace = " %s\\n" % single
	else:
		whitespace = " "
	return "%s/%s%s" % ( single, glyphname, whitespace )

for pair in pairsOrSingles:
	if len(pair) == 2: # it really is a pair
		for i, x in enumerate(lowercase):
			lower += pairAddition( i, pair, x, linelength=15 )
		for i, x in enumerate(uppercase):
			upper += pairAddition( i, pair, x, linelength=15 )
		for i, n in enumerate(fig):
			number += pairAddition( i, pair, n )
			
	else: # is a single
		for i, x in enumerate(lowercase):
			lower += singleAddition( i, pair, x, linelength=15 )
		for i, x in enumerate(uppercase):
			upper += singleAddition( i, pair, x, linelength=15 )
		for i, n in enumerate(fig):
			number += singleAddition( i, pair, n )
		lower += pair
		upper += pair
		number += pair
		
	lower  += "\n"
	upper  += "\n"
	number += "\n"

Glyphs.clearLog()
Glyphs.showMacroWindow()

print lower
print upper
print number

from AppKit import *

def setClipboard( myText ):
	"""
	Sets the contents of the clipboard to myText.
	Returns True if successful, False if unsuccessful.
	"""
	try:
		myClipboard = NSPasteboard.generalPasteboard()
		myClipboard.declareTypes_owner_( [NSStringPboardType], None )
		myClipboard.setString_forType_( myText, NSStringPboardType )
		return True
	except Exception as e:
		return False

if not setClipboard(lower+upper+number):
	print "Warning: could not set clipboard to %s" % ( "clipboard text" )

newline="""
"""
#Doc = Glyphs.currentDocument
thisFont.newTab( lower.replace( "\\n",newline ).replace( newline+newline, newline ) )
thisFont.newTab( upper.replace( "\\n",newline ).replace( newline+newline, newline ) )
thisFont.newTab( number.replace( "\\n",newline ).replace( newline+newline, newline ) )

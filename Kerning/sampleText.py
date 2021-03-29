# -*- coding: utf-8 -*-
from __future__ import print_function
from GlyphsApp import Glyphs
from AppKit import NSNotFound
from collections import OrderedDict

def setSelectSampleTextIndex( thisFont, tab=None, marker="### CUSTOM KERN STRING ###"):
	if Glyphs.versionNumber >= 3:
		# Glyphs 3 code
		sampleTexts = OrderedDict([(d['name'], d['text']) for d in Glyphs.defaults["SampleTextsList"]])

		foundSampleString = False
		for sampleTextIndex, k in enumerate(sampleTexts.keys()):
			if marker in k:
				foundSampleString = True
				if not tab:
					tab = thisFont.currentTab
					if not tab:
						tab = thisFont.newTab()
				tab.selectSampleTextArrayController().setSelectionIndex_(sampleTextIndex+1)
				tab.text = sampleTexts[sampleTexts.keys()[sampleTextIndex+1]]
				break

		if not foundSampleString:
			print("Warning: Could not find '%s' in sample strings." % marker)
	else:
		# Glyphs 2 code
		sampleTexts = tuple(Glyphs.defaults["SampleTexts"])

		sampleTextIndex = sampleTexts.index(marker)
		if sampleTextIndex > -1:
			if not tab:
				tab = thisFont.currentTab
				if not tab:
					tab = thisFont.newTab()
			tab.selectSampleTextArrayController().setSelectionIndex_(sampleTextIndex+1)
			tab.text = sampleTexts[sampleTextIndex+1]
		else:
			print("Warning: Could not find '%s' in sample strings." % marker)

def addToSampleText( kernStrings, marker="### CUSTOM KERN STRING ###"):
	if kernStrings is None:
		print("No kern strings generated.")
		return False
	else:
		# Get current sample texts:
		if Glyphs.versionNumber >= 3:
			# Glyphs 3 code
			sampleTexts = Glyphs.defaults["SampleTextsList"].mutableCopy()	

			# clear old kerning strings
			indexesToRemove = []
			for index, sampleText in enumerate(sampleTexts):
				if sampleText["name"] == marker:
					indexesToRemove += [index]
			for index in reversed(indexesToRemove):
				sampleTexts.removeObjectAtIndex_(index)

			sampleTexts.append(dict(name=marker,text="\n".join(kernStrings)))
			Glyphs.defaults["SampleTextsList"] = sampleTexts
			return True
		else:
			# Glyphs 2 code
			sampleTexts = Glyphs.defaults["SampleTexts"].mutableCopy()
			kernStringValues = kernStrings
			# Cut off after marker text:
			i = sampleTexts.indexOfObject_(marker)
			if i == NSNotFound:
				print("Warning: Could not find this marker:\n%s\nAppending it..." % marker)
				sampleTexts.append(marker)
			else:
				sampleTexts = sampleTexts[:i+1]
		
			# Add new kern strings to the list:
			if len(kernStringValues) > 0:
				sampleTexts.extend(kernStringValues)
			else:
				return False
		
			# Exchange the stored Sample Texts with the new ones:
			Glyphs.defaults["SampleTexts"] = sampleTexts
			return True

def buildKernStrings( listOfLeftGlyphNames, listOfRightGlyphNames, thisFont=None, linePrefix="nonn", linePostfix="noon" ):
	"""Takes a list of glyph names and returns a list of kernstrings"""
	if thisFont is None:
		print("No font detected.")
		return None
	else:
		kernStrings = []
	
		# collect left names/groups:
		leftGroups = []
		for leftName in listOfLeftGlyphNames:
		
			# Hardcoded changes to prevent Æ/æ from appearing instead of E/e:
			if leftName == "ae" and thisFont.glyphs["ae"].rightKerningGroup == thisFont.glyphs["e"].rightKerningGroup:
				leftName = "e"
			if leftName == "ae.sc" and thisFont.glyphs["ae.sc"].rightKerningGroup == thisFont.glyphs["e.sc"].rightKerningGroup:
				leftName = "e.sc"
			if leftName == "AE" and thisFont.glyphs["AE"].rightKerningGroup == thisFont.glyphs["E"].rightKerningGroup:
				leftName = "E"
		
			leftGroup = thisFont.glyphs[leftName].rightKerningGroup
			if (leftGroup is not None) and (not leftGroup in leftGroups):
				leftGroups.append( leftGroup )
			
				# collect right names/groups:
				rightGroups = []
				for rightName in listOfRightGlyphNames:
				
					# Hardcoded changes:
					if rightName == "idotless" and thisFont.glyphs["idotless"].leftKerningGroup == thisFont.glyphs["n"].leftKerningGroup:
						rightName = "n"
					if rightName == "idotless" and thisFont.glyphs["idotless"].leftKerningGroup == thisFont.glyphs["i"].leftKerningGroup:
						rightName = "i"
					if rightName == "jdotless" and thisFont.glyphs["jdotless"].leftKerningGroup == thisFont.glyphs["j"].leftKerningGroup:
						rightName = "j"
					
					rightGroup = thisFont.glyphs[rightName].leftKerningGroup
					if (rightGroup is not None) and (not rightGroup in rightGroups):
						rightGroups.append( rightGroup )
						kernString = "%s/%s/%s %s" % ( linePrefix, leftName, rightName, linePostfix )
						kernStrings += [ kernString ]
		return kernStrings

def executeAndReport( kernStrings ):
	# brings macro window to front and clears its log:
	# Glyphs.clearLog()
	Glyphs.showMacroWindow()
	
	# print status and modify Sample Texts:
	print("Adding %i lines to Sample Texts..." % len( kernStrings ))
	if not addToSampleText( kernStrings ):
		print("Warning: could not add the lines.")
	else:
		print("Done.")
	

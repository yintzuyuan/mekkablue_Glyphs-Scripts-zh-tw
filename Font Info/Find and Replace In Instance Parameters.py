#MenuTitle: Find and Replace in Instance Parameters
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds and Replace in Custom Parameters of selected instances of the current font or project file.
"""

import vanilla
from Foundation import NSUserDefaults, NSString

class FindAndReplaceInInstanceParameters(object):

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 180
		windowWidthResize = 300 # user can resize width by this value
		windowHeightResize = 400 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Find and Replace In Instance Parameters", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName="com.mekkablue.FindAndReplaceInInstanceParameters.mainwindow" # stores last window position and size
			)

		# UI elements:
		self.w.text_1 = vanilla.TextBox((15 - 1, 12 + 2, 130, 14), "Replace in parameters", sizeStyle='small')
		self.w.availableParameters = vanilla.PopUpButton((145, 12, -15, 17), self.setAvailableParameters(None), callback=self.SavePreferences, sizeStyle='small')
		self.w.find = vanilla.TextEditor((15, 40, 100, -50), text="find", callback=self.SavePreferences, checksSpelling=False)
		self.w.replace = vanilla.TextEditor((110, 40, 100, -50), text="replace", callback=self.SavePreferences, checksSpelling=False)
		self.windowResize(None)

		# Run Button:
		self.w.rescanButton = vanilla.Button((-200, -20 - 15, -110, -15), "Rescan", sizeStyle='regular', callback=self.setAvailableParameters)
		self.w.runButton = vanilla.Button((-80 - 15, -20 - 15, -15, -15), "Replace", sizeStyle='regular', callback=self.FindAndReplaceInInstanceParametersMain)
		self.w.setDefaultButton(self.w.runButton)

		self.w.bind("resize", self.windowResize)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Find and Replace In Instance Parameters' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def windowResize(self, sender):
		windowWidth = self.w.getPosSize()[2]
		adaptedWidth = windowWidth / 2 - 20
		self.w.find.setPosSize((15, 40, adaptedWidth, -50))
		self.w.replace.setPosSize((-adaptedWidth - 15, 40, adaptedWidth, -50))

	def SavePreferences(self, sender):
		try:
			Glyphs.defaults["com.mekkablue.FindAndReplaceInInstanceParameters.availableParameters"] = self.w.availableParameters.get()
			Glyphs.defaults["com.mekkablue.FindAndReplaceInInstanceParameters.find"] = self.w.find.get()
			Glyphs.defaults["com.mekkablue.FindAndReplaceInInstanceParameters.replace"] = self.w.replace.get()
		except:
			return False

		return True

	def LoadPreferences(self):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.FindAndReplaceInInstanceParameters.availableParameters": "0",
					"com.mekkablue.FindAndReplaceInInstanceParameters.find": "",
					"com.mekkablue.FindAndReplaceInInstanceParameters.replace": ""
					}
				)
			self.w.find.set(Glyphs.defaults["com.mekkablue.FindAndReplaceInInstanceParameters.find"])
			self.w.replace.set(Glyphs.defaults["com.mekkablue.FindAndReplaceInInstanceParameters.replace"])
			self.w.availableParameters.set(Glyphs.defaults["com.mekkablue.FindAndReplaceInInstanceParameters.availableParameters"])
		except:
			return False

		return True

	def getInstances(self):
		# get instances from project or font:
		frontmostDoc = Glyphs.orderedDocuments()[0]
		if frontmostDoc.isKindOfClass_(GSProjectDocument):
			return frontmostDoc.instances()
		elif Glyphs.font:
			return Glyphs.font.instances
		else:
			return None

	def setAvailableParameters(self, sender):
		instances = self.getInstances()
		if instances:
			# collect parameters:
			parameters = []
			for thisInstance in instances:
				for thisParameter in thisInstance.customParameters:
					parameters.append(thisParameter.name)
			# avoid duplicates:
			parameters = list(set(parameters))

			if sender:
				# Rescan button
				self.w.availableParameters.setItems(sorted(parameters))
				self.w.availableParameters.set(0)
			else:
				# sort and return:
				return sorted(parameters)
		else:
			return None

	def FindAndReplaceInInstanceParametersMain(self, sender):
		try:
			instances = self.getInstances()
			parameterName = self.w.availableParameters.getItems()[self.w.availableParameters.get()]
			findText = self.w.find.get()
			replaceText = self.w.replace.get()

			if parameterName and instances:
				for thisInstance in instances: # loop through instances
					parameter = thisInstance.customParameters[parameterName]
					if not parameter is None:
						print(type(parameter))
						if type(parameter) in (bool, objc._pythonify.OC_PythonInt):
							onOff = False
							if replaceText.lower() in ("1", "yes", "on", "an", "ein", "ja", "true", "wahr"):
								onOff = True
							thisInstance.customParameters[parameterName] = onOff
							onOrOff = "on" if onOff else "off"
							print("%s: switched %s %s" % (thisInstance.name, onOrOff, parameterName))

						elif findText:
							if type(parameter) in (objc.pyobjc_unicode, NSString, str, unicode):
								thisInstance.customParameters[parameterName] = parameter.replace(findText, replaceText)
							elif hasattr(parameter, "__add__") and hasattr(parameter, "__delitem__"):
								findList = findText.splitlines()
								replaceList = replaceText.splitlines()
								for findItem in findList:
									while findItem in parameter:
										parameter.remove(findItem)
								for replaceItem in replaceList:
									parameter.append(replaceItem)
								thisInstance.customParameters[parameterName] = parameter
							print("%s: replaced in %s" % (thisInstance.name, parameterName))

						elif replaceText:
							if type(parameter) in (objc.pyobjc_unicode, NSString, str, unicode):
								thisInstance.customParameters[parameterName] += replaceText
							elif hasattr(parameter, "__add__"):
								replaceList = replaceText.splitlines()
								for replaceItem in replaceList:
									parameter.append(replaceItem)
								thisInstance.customParameters[parameterName] = parameter
							print("%s: appended to %s" % (thisInstance.name, parameterName))

			if not self.SavePreferences(self):
				print("Note: 'Find and Replace In Instance Parameters' could not write preferences.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Find and Replace In Instance Parameters Error: %s" % e)
			import traceback
			print(traceback.format_exc())

FindAndReplaceInInstanceParameters()

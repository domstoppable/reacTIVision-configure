import sys, kivy

kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse
from kivy.graphics.instructions import InstructionGroup

class TouchConfiguration(App):
	def __init__(self, simple=True):
		super(TouchConfiguration, self).__init__()
		self.simple = simple
		if simple:
			self.calibrationSize = (5, 4)
		else:
			self.calibrationSize = (9, 7)

	def build(self):
		self.widget = TouchConfigurationWidget(self.calibrationSize)
		return self.widget

	def on_stop(self):
		if self.widget.calibrating: return

		outputFile = open("calibration.grid", "w")
		if self.simple:
			rawData = self.widget.offsetData
			data = [[None for y in range(7)] for x in range(9)]
			for x in range(9):
				for y in range(7):
					if x % 2 == 0 and y % 2 == 0:
						data[x][y] = rawData[x/2][y/2]
					elif y % 2 == 0:
						data[x][y] = [
							(rawData[x/2][y/2][0] + rawData[x/2 + 1][y/2][0]) / 2,
							(rawData[x/2][y/2][1] + rawData[x/2 + 1][y/2][1]) / 2
						]
					elif x % 2 == 0:
						data[x][y] = [
							(rawData[x/2][y/2][0] + rawData[x/2][y/2 + 1][0]) / 2,
							(rawData[x/2][y/2][1] + rawData[x/2][y/2 + 1][1]) / 2
						]
					else:
						data[x][y] = [
							rawData[x/2][y/2][0],
							rawData[x/2][y/2][1]
						]
						data[x][y][0] += rawData[x/2 + 1][y/2][0]
						data[x][y][1] += rawData[x/2 + 1][y/2][1]
						data[x][y][0] += rawData[x/2][y/2 + 1][0]
						data[x][y][1] += rawData[x/2][y/2 + 1][1]
						data[x][y][0] += rawData[x/2 + 1][y/2 + 1][0]
						data[x][y][1] += rawData[x/2 + 1][y/2 + 1][1]

						data[x][y][0] /= 4
						data[x][y][1] /= 4
		else:
			data = self.widget.offsetData

		for y in range(7):
			yIndex = 6 - y
			for x in range(9):
				expectedLocation = self.widget._getExpectedPosition([x, yIndex], [9, 7])
				xData = (data[x][yIndex][0] - expectedLocation[0]) / (self.widget.width / 9)
				yData = -(data[x][yIndex][1] - expectedLocation[1]) / (self.widget.height / 7)

				outputFile.write("%f %f\n" % (xData, yData))
		for i in range(17):
			outputFile.write("0 0\n")

		outputFile.close()

class TouchConfigurationWidget(Widget):
	def __init__(self, calibrationSize):
		super(TouchConfigurationWidget, self).__init__()
		self.calibrationSize = calibrationSize
		self.currentPosition = [0, 0]
		self.offsetData = [[None for y in range(self.calibrationSize[1])] for x in range(self.calibrationSize[0])]
		self.calibrating = True
		self.calibrationTouch = None
		self.savePointInstructionGroup = None

		self.timerDisplay = Label(text="", font_size=256)
		self.add_widget(self.timerDisplay)
		self._updateView()

	def _touchTimer(self, dt):
		self.touchTimer -= 1
		if self.calibrationTouch == None:
			self.touchTimer = 0
			self.timerDisplay.text = ""
			return False
		if self.touchTimer <= 0:
			self.touchTimer = 0
			self.timerDisplay.text = ""
			self._saveTouch()
			return False
		else:
			self.timerDisplay.text = "%d" % self.touchTimer

		return True

	def on_touch_down(self, touch):
		if not self.calibrating:
			with self.canvas:
				Color(0, 0.75, 0.75, 0.5)
				self._drawCircle([touch.x, touch.y], 25)
		elif self.calibrationTouch == None:
			self.calibrationTouch = touch
			self.touchTimer = 3
			self.timerDisplay.text = "%d" % self.touchTimer
			self.timerDisplay.pos = [0,0]
			self.timerDisplay.size = [self.width, self.height]


			Clock.schedule_interval(self._touchTimer, 0.5)

	def on_touch_up(self, touch):
		if self.calibrationTouch == touch:
			self.calibrationTouch = None
			self.timerDisplay.text = ""
			Clock.unschedule(self._touchTimer)

	def _saveTouch(self):
		if not self.calibrating: return
		if self.calibrationTouch == None: return

		expectedLocation = self._getExpectedPosition()

		self.canvas.remove(self.savePointInstructionGroup)
		self.savePointInstructionGroup = None
		self.canvas.add(Color(0, 1, 0))
		self._drawCircle(expectedLocation, 25)

		self.offsetData[self.currentPosition[0]][self.currentPosition[1]] = [self.calibrationTouch.x, self.calibrationTouch.y]

		# update data
		self.currentPosition[0] += 1
		if self.currentPosition[0] >= self.calibrationSize[0]:
			self.currentPosition[0] = 0
			self.currentPosition[1] += 1
			if self.currentPosition[1] >= self.calibrationSize[1]:
				self.calibrating = False

		self.touchAccepted = False
		self.calibrationTouch = None
		self._updateView()

	def _updateView(self):
		if not self.calibrating:
			pass
		else:
			location = self._getExpectedPosition()

			if self.savePointInstructionGroup == None:
				self.savePointInstructionGroup = InstructionGroup()
				self.savePointInstructionGroup.add(Color(1, 0, 0))
				self._drawCircle(location, 100, self.savePointInstructionGroup)
				self.savePointInstructionGroup.add(Color(0, 0, 0))
				self._drawCircle(location, 66, self.savePointInstructionGroup)
				self.savePointInstructionGroup.add(Color(1, 1, 1))
				self._drawCircle(location, 33, self.savePointInstructionGroup)

				self.canvas.add(self.savePointInstructionGroup)

	def _getExpectedPosition(self, point=None, calibrationSize=None):
		if point == None: point = self.currentPosition
		if calibrationSize == None: calibrationSize = self.calibrationSize

		return [
			self.width * (float(point[0]) / (calibrationSize[0] - 1)),
			self.height * (float(point[1]) / (calibrationSize[1] - 1))
		]

	def _drawCircle(self, location, size, instructionGroup=None):
		[x,y] = location
		pos = (x - size/2, y - size/2)
		size = (size, size)

		if instructionGroup != None:
			instructionGroup.add(Ellipse(pos=pos, size=size))
		else:
			self.canvas.add(Ellipse(pos=pos, size=size))

if __name__ == '__main__':
	if (len(sys.argv) > 1):
		TouchConfiguration(sys.argv[1].lower() != "detailed").run()
	else:
		TouchConfiguration().run()

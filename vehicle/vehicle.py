"""
Basado en https://github.com/alex-drake/OpenCV-Traffic-Counter/blob/master/trafficCounter/blobDetection.py

"""
import datetime
from utils.utils import find_nearest

class Vehicle(object):
	def __init__(self, vehicleId, vehicleClass, position, frame, timestamp):
		self.id = vehicleId
		self.vehicle_class = vehicleClass
		self.positions = [position]
		self.timestamps = [timestamp]
		self.timeRef = {"A": 0, "B": 0, "C": 0, "D": 0}
		self.pixelRef = {"A": None, "B": None, "C": None, "D": None}
		self.frames_since_seen = 0
		self.frames_seen = 0
		self.frame_last_seen = frame
		self.counted = False
		self.direction = 0
		self.speed = 0
		self.speedReady = False


	def last_position(self):
		return self.positions[-1]


	def add_position(self, new_position, frame):
		self.positions.append(new_position)
		self.timestamps.append(datetime.datetime.now())
		self.frames_since_seen = 0
		self.frames_seen += 1
		self.frame_last_seen = frame
	

	def find_references(self):
		# Tenemos que separar las coordenadas (X, Y) de tuplas en listas independientes.
		xPositions, yPositions = zip(*self.positions)

		# Buscamos dentro del array el ID más cercano a la referencia del punto A.
		arrayId = find_nearest(xPositions, 790)
		# Y agregamos al diccionario tanto la posición como la referencia temporal.
		self.pixelRef["A"] = xPositions[arrayId]
		self.timeRef["A"] = self.timestamps[arrayId]

		# Buscamos dentro del array el ID más cercano a la referencia del punto B.
		arrayId = find_nearest(xPositions, 740)
		# Y agregamos al diccionario tanto la posición como la referencia temporal.
		self.pixelRef["B"] = xPositions[arrayId]
		self.timeRef["B"] = self.timestamps[arrayId]

		# Buscamos dentro del array el ID más cercano a la referencia del punto C.
		arrayId = find_nearest(xPositions, 670)
		# Y agregamos al diccionario tanto la posición como la referencia temporal.
		self.pixelRef["C"] = xPositions[arrayId]
		self.timeRef["C"] = self.timestamps[arrayId]

		# Buscamos dentro del array el ID más cercano a la referencia del punto D.
		arrayId = find_nearest(xPositions, 590)
		# Y agregamos al diccionario tanto la posición como la referencia temporal.
		self.pixelRef["D"] = xPositions[arrayId]
		self.timeRef["D"] = self.timestamps[arrayId]
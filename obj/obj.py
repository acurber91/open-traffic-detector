"""
Basado en https://github.com/alex-drake/OpenCV-Traffic-Counter/blob/master/trafficCounter/blobDetection.py

"""
import datetime
from utils.utils import find_nearest

class ObjectToTrack(object):
	def __init__(self, vehicleId, vehicleClass, position, frame, timestamp):
		self.id = vehicleId
		self.object_class = vehicleClass
		self.positions = [position]
		self.timestamps = [timestamp]
		self.time_ref = {"A": 0, "B": 0, "C": 0, "D": 0}
		self.pixel_ref = {"A": None, "B": None, "C": None, "D": None}
		self.frames_since_seen = 0
		self.frames_seen = 0
		self.frame_last_seen = frame
		self.counted = False
		self.direction = 0
		self.speed = 0
		self.speed_ready = False


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
		x_positions, y_positions = zip(*self.positions)

		# Buscamos dentro del array el ID más cercano a la referencia del punto A.
		array_id = find_nearest(x_positions, 790)
		# Y agregamos al diccionario tanto la posición como la referencia temporal.
		self.pixel_ref["A"] = x_positions[array_id]
		self.time_ref["A"] = self.timestamps[array_id]

		# Buscamos dentro del array el ID más cercano a la referencia del punto B.
		array_id = find_nearest(x_positions, 740)
		# Y agregamos al diccionario tanto la posición como la referencia temporal.
		self.pixel_ref["B"] = x_positions[array_id]
		self.time_ref["B"] = self.timestamps[array_id]

		# Buscamos dentro del array el ID más cercano a la referencia del punto C.
		array_id = find_nearest(x_positions, 670)
		# Y agregamos al diccionario tanto la posición como la referencia temporal.
		self.pixel_ref["C"] = x_positions[array_id]
		self.time_ref["C"] = self.timestamps[array_id]

		# Buscamos dentro del array el ID más cercano a la referencia del punto D.
		array_id = find_nearest(x_positions, 590)
		# Y agregamos al diccionario tanto la posición como la referencia temporal.
		self.pixel_ref["D"] = x_positions[array_id]
		self.time_ref["D"] = self.timestamps[array_id]
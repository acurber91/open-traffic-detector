"""
	Open Traffic Monitor: Simple and Realtime Traffic Monitor
	Copyright (C) 2020-2021 - Agustin Curcio Berardi

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.

	Based on: https://github.com/alex-drake/OpenCV-Traffic-Counter/blob/master/trafficCounter/blobDetection.py
"""

import datetime
from utils.utils import find_nearest

class ObjectToTrack(object):
	"""
	This class represent the objects that are going to be tracked.
	"""
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
		"""
		Just returns the last position of the object.
		"""
		return self.positions[-1]


	def add_position(self, new_position, frame):
		"""
		Adds a new position to the object's position array.
		"""
		self.positions.append(new_position)
		self.timestamps.append(datetime.datetime.now())
		self.frames_since_seen = 0
		self.frames_seen += 1
		self.frame_last_seen = frame
	

	def find_references(self):
		"""
		Finds the closest references from the object's position array.
		"""
		x_positions, y_positions = zip(*self.positions)

		# Nearest reference to point A.
		array_id = find_nearest(x_positions, 790)
		self.pixel_ref["A"] = x_positions[array_id]
		self.time_ref["A"] = self.timestamps[array_id]

		# Nearest reference to point B.
		array_id = find_nearest(x_positions, 740)
		self.pixel_ref["B"] = x_positions[array_id]
		self.time_ref["B"] = self.timestamps[array_id]

		# Nearest reference to point C.
		array_id = find_nearest(x_positions, 670)
		self.pixel_ref["C"] = x_positions[array_id]
		self.time_ref["C"] = self.timestamps[array_id]

		# Nearest reference to point D.
		array_id = find_nearest(x_positions, 590)
		self.pixel_ref["D"] = x_positions[array_id]
		self.time_ref["D"] = self.timestamps[array_id]
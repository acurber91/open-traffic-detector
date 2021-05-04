"""
	Open Traffic Detector: Simple and Realtime Traffic Monitor
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

import cv2
import datetime
import numpy as np

from utils.utils import calculate_centroid
from obj.obj import ObjectToTrack

class ObjectCounter(object):
	"""
	This class is used to keep track and count all the previously identified objects.
	"""

	def __init__(self, videoStream):
		self.objects = []
		self.object_count = 0
		self.objects_one_way = 0
		self.objects_other_way = 0
		self.current_frame = 0
		self.video = videoStream
		self.max_unwatch_frames = 2
		self.to_save = []
	

	def check_object_counted(self, objectId):
		"""
		Takes and object ID and returns its position if positive.
		"""
		for obj in self.objects:
			if obj.id == objectId:
				return obj
		return None
	

	def append_object(self, newObject):
		"""
		Just appends new objects to the objects array.
		"""
		newObject.counted = True
		newObject.frames_seen += 1
		self.objects.append(newObject)
		self.object_count += 1
	

	def update_all_frames(self):
		"""
		Updates the frame counter of each one of the tracked objects.
		"""
		if self.objects:
			for obj in self.objects:
				obj.frames_since_seen += 1


	def delete_object(self, index):
		"""
		Removes an object from the tracked object array.
		"""
		self.objects.pop(index)
		self.object_count -= 1
	

	def save_object(self, index):
		"""
		Stores all the object information into a dictionary for later processing.
		"""
		if(self.objects[index].speed > 0):
			y = {
				"id": str(self.objects[index].id), 
				"position": str(self.objects[index].positions[-1]),
				"timestamp": str(self.objects[index].timestamps[-1].strftime('%d/%m/%Y %H:%M:%S')),
				"direction": str(self.objects[index].direction),
				"speed": str(self.objects[index].speed),
				"class": str(self.objects[index].object_class)
				}
			self.to_save.append(y)
	

	def update(self, tracked_objects, verbose):
		"""
		Updates the status of all the tracked objects along with all their parameters.
		"""
		# Get the current frame number.
		self.current_frame = self.video.get(cv2.CAP_PROP_POS_FRAMES)
		
		# Check if the object is already tracked or not.
		if tracked_objects.size != 0:
			for obj in tracked_objects:
				tracked_id = int(obj[4])
				object_class = int(obj[5])
				# Calculate the centroid.
				new_position = calculate_centroid(obj[0], obj[1], obj[2], obj[3])
				# Check if it is counted.
				search_result = self.check_object_counted(tracked_id)
				# If not, it is added to the tracked object array.
				if search_result is None:
					new_car = ObjectToTrack(tracked_id, object_class, new_position, self.current_frame, datetime.datetime.now())
					self.append_object(new_car)
				else:
					# If it is counted, then all its parameters are updated.
					for obje in self.objects:
						if obje.id == search_result.id:
							obje.add_position(new_position, self.current_frame)
						else:
							if obje.frame_last_seen != self.current_frame:
								obje.frames_since_seen += 1
		
		# If no objects where retrieved from the tracker, the frame counter for all the objects is updated.
		else:
			self.update_all_frames()

		# And since this function has to run frequently, the status of all the objects is updated.
		for obj in self.objects:
			# Check if there are objects to be deleted.
			if obj.frames_since_seen > self.max_unwatch_frames:
				self.save_object(self.objects.index(obj))
				self.delete_object(self.objects.index(obj))
			# Check if direction can be calculated.
			if obj.frames_seen > 5 and obj.direction == 0:
				print("[INFO]   Object class:", obj.object_class)
				# An auxiliary array to store all the centroids.
				x = []
				for p in obj.positions:
					x.append(p[0])
				if (int(obj.last_position()[0]) - int(np.mean(x))) > 0:
					# Left to right direction.
					obj.direction = 1
					self.objects_one_way += 1
					print("[INFO]   Direction: ----->")
				else:
					# Right to left direction.
					obj.direction = 2
					self.objects_other_way += 1
					print("[INFO]   Direction: <-----")
			
			# If the direction could be calculated, then speed can also be determined based on position and time references.
			if obj.direction == 1:
				if obj.last_position()[0] > 850:
					if not(obj.speed_ready):
						obj.find_references()
						if verbose:
							print("[DEBUG]  Point A:", obj.pixel_ref["A"], ", Timestamp:", obj.time_ref["A"])
							print("[DEBUG]  Point B:", obj.pixel_ref["B"], ", Timestamp:", obj.time_ref["B"])
							print("[DEBUG]  Point C:", obj.pixel_ref["C"], ", Timestamp:", obj.time_ref["C"])
							print("[DEBUG]  Point D:", obj.pixel_ref["D"], ", Timestamp:", obj.time_ref["D"])
						obj.speed_ready = True

			elif obj.direction == 2:
				if obj.last_position()[0] < 530:
					if not(obj.speed_ready):
						obj.find_references()
						if verbose:
							print("[DEBUG]  Point A:", obj.pixel_ref["A"], ", Timestamp:", obj.time_ref["A"])
							print("[DEBUG]  Point B:", obj.pixel_ref["B"], ", Timestamp:", obj.time_ref["B"])
							print("[DEBUG]  Point C:", obj.pixel_ref["C"], ", Timestamp:", obj.time_ref["C"])
							print("[DEBUG]  Point D:", obj.pixel_ref["D"], ", Timestamp:", obj.time_ref["D"])

						obj.speed_ready = True

			# And calculate the speed using the found references.
			if obj.speed_ready and obj.speed == 0:
				calculated_speed = []
				i = "A"
				j = chr(ord(i) + 1)
				if obj.direction == 2:
					while j != "E":
						distance_diff = (obj.pixel_ref[i] - obj.pixel_ref[j]) * 0.0087 # Meters by pixel.
						time_diff = abs(obj.time_ref[j].timestamp() - obj.time_ref[i].timestamp())
						try:
							velocity = (distance_diff / time_diff) * 3.6 # m/s to km/h conversion.
							calculated_speed.append(round(velocity, 2))
						except ZeroDivisionError:
							calculated_speed.append(-1) # Speed could not be calculated.
						i = chr(ord(i) + 1)
						j = chr(ord(j) + 1)
				elif obj.direction == 1:
					while j != "E":
						distance_diff = (obj.pixel_ref[i] - obj.pixel_ref[j]) * 0.0087 # Meters by pixel.
						time_diff = abs(obj.time_ref[i].timestamp() - obj.time_ref[j].timestamp())
						try:
							velocity = (distance_diff / time_diff) * 3.6 # m/s to km/h conversion.
							calculated_speed.append(round(velocity, 2))
						except ZeroDivisionError:
							calculated_speed.append(-1) # Speed could not be calculated.
						i = chr(ord(i) + 1)
						j = chr(ord(j) + 1)
				if verbose:
					print("[DEBUG]  Estimated speed:", calculated_speed)
				obj.speed = round(np.average(calculated_speed), 2)
				print("[INFO]   Speed:", obj.speed, "km/h")
				
				# And show the object count.
				print("[INFO]   Counted objects:", self.object_count)
		
		# If there are objects to store, then return them.
		if self.to_save:
			return(self.to_save.pop())
		else:
			return(None)
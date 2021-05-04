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
"""

import cv2
import numpy as np
import math
import yaml

from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from sort.sort import Sort
from tracker.tracker import ObjectCounter
from utils.utils import *
from reporter.reporter import Reporter
from mqtt.mqtt import MqttClient


def main():
	"""
	Main function of the Open Traffic Monitor.
	"""
	
	# The configuration file is read. The content of the YAML file is loaded into a dictionary.
	config = yaml.safe_load(open("./config.yml"))

	# The labels file is read. Will be used by the Edge TPU detector.
	labels = read_label_file(config["input"]["labels"]) if config["input"]["labels"] else {}

	# TensorFlow Lite interpreter for the Edge TPU is initialized with the selected model.
	interpreter = make_interpreter(config["input"]["model"])

	# Allocate memory for the model's input tensors.
	interpreter.allocate_tensors()

	# Find the model's input width and height.
	model_size = interpreter.get_input_details()
	model_height = model_size[0]['shape'][1]
	model_width = model_size[0]['shape'][2]

	# The SORT class object is instantiated.
	tracker = Sort(max_age = config["tracker"]["max_age"], min_hits = config["tracker"]["min_hits"], iou_threshold = config["tracker"]["iou_threshold"])

	# Setup the video stream.
	videoStream = cv2.VideoCapture(config["input"]["source"])

	# The ObjectCounter class object is instantiated.
	counter = ObjectCounter(videoStream)

	# The Reporter class object is instantiated.
	reporter = Reporter(config["result"]["logs"])

	# The MqttClient class object is instantiated.
	client = MqttClient(config["mqtt"]["broker"], config["mqtt"]["port"])

	# The while loop is executed until a SIGINT is received.
	try:
		while True:		
			
			# Each one of the video frames will be processed.
			ret, frame = videoStream.read()

			if not(ret):
				print("[ERROR] The video frame could not be read.")
				break
			
			# Input image width and height is retrieved.
			input_height, input_width = frame.shape[:2]

			# And used to calculate the scale factors needed to properly show the resulting video.
			scaling_factor_x = model_width / input_width
			scaling_factor_y = model_height / input_height

			# Vector that will store the objects identities assigned by the tracker.
			tracked_objs = np.empty((0, 5))

			# Vector that will store the objects found by the detector.
			detected_objs = np.empty((0, 5))

			# Vector that will store objects identities as well as their classes.
			completed_objs = np.empty((0, 6))
				
			# Each frame is resized to meet the model requirements.
			new_frame = cv2.resize(frame, (model_height, model_width), interpolation = cv2.INTER_AREA)
			
			# And copy that into the input tensors.
			common.set_input(interpreter, new_frame)

			# Run the inference model.
			interpreter.invoke()

			# And find if there are objects in the frame.
			objs = detect.get_objects(interpreter, config["detector"]["threshold"], (scaling_factor_x, scaling_factor_y))

			# If there are, then we need to prepare the vectors.
			if objs:
				for obj in objs:
					# We are only intrested in two types of object classes: "car" or "truck".
					if(obj.id == 2 or obj.id == 7):
						# In these two vectors, we need to append boxes coordinates, their scores and their classes.
						tracked_objs = np.append(tracked_objs, np.array([[obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax, obj.score]]), axis=0)
						detected_objs = np.append(detected_objs, np.array([[obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax, obj.id]]), axis=0)
			
			if tracked_objs.size != 0:
				# And if the detected objects vector is not empty, then it is shared with the tracker.
				trackers = tracker.update(tracked_objs)
			else:
				# Otherwise the tracker object requires an empty vector.
				trackers = tracker.update(np.empty((0, 5)))
			
			# Having both the objects classes and their IDs, we need to match them. To do that, the euclidean distance is used.
			if trackers.size != 0:
				for track in trackers:
					tracked_box = calculate_centroid(track[0], track[1], track[2], track[3])
					for detected_obj in detected_objs:
						detected_box = calculate_centroid(detected_obj[0], detected_obj[1], detected_obj[2], detected_obj[3])
						distance = math.sqrt(pow(tracked_box[0] - detected_box[0], 2) + pow(tracked_box[1] - detected_box[1], 2))
						if distance <= 10: # A maximum difference of 10 pixels is admitted between detections and tracks.
							completed_objs = np.append(completed_objs, np.array([[track[0], track[1], track[2], track[3], track[4], detected_obj[4]]]), axis=0)
				
			# After matching the detections to the tracks, we send that information to the object counter.
			objToSave = counter.update(completed_objs, config["result"]["verbose"])

			# If there are objects to save, then we save them.
			if(objToSave != None):
				reporter.data_save(objToSave)
				client.publish(config["mqtt"]["topic"], objToSave)
								
			# In case the user wants analyze the video output, then we show it.
			if config["result"]["output"]:
				draw_objects(frame, objs, labels)
				if trackers.size != 0:
					cv2.putText(frame, '%.2f' % (trackers[0, 4]), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
				
				# A window for the video is opened.
				cv2.imshow("Detections", frame)

				# Each of the frames will be shown for at least 1 millisecond.
				cv2.waitKey(1)

	except KeyboardInterrupt:
		# Clean up
		cv2.destroyAllWindows()
		videoStream.release()
		client.disconnect()
		print("[INFO]   Exiting gracefully. Bye!")
	
if __name__ == '__main__':
	main()
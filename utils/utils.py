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
"""

import numpy as np
import cv2

def calculate_centroid(x1, y1, x2, y2):
	"""
	Calculates the centroid of a rectangle based on two corners coordinates.
	"""
	return(int((x1 + x2)/2), int((y1 + y2)/2))


def find_nearest(array, value):
	"""
	Find the nearest array object for a certain value.
	"""
	array = np.asarray(array)
	id_x = (np.abs(array - value)).argmin()
	return id_x


def draw_objects(img, objs, labels):
	"""
	Draws a bounding box and label for each object.
	"""
	for obj in objs:
		if obj.id == 2 or obj.id == 3 or obj.id == 7:
			bbox = obj.bbox
			cv2.rectangle(img, (bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax), (0, 255, 0), 1)
			(label_width, label_height), baseline = cv2.getTextSize(labels.get(obj.id, obj.id), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
			cv2.rectangle(img, (bbox.xmin, bbox.ymin), (bbox.xmin + label_width + 20, bbox.ymin + 4*label_height), (0, 255, 0), -1)
			cv2.putText(img, '%s' % (labels.get(obj.id, obj.id).capitalize()), (bbox.xmin + 10, bbox.ymin + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
			cv2.putText(img, '%.2f' % (obj.score), (bbox.xmin + 10, bbox.ymin + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
import numpy as np
import cv2

def calculate_centroid(x1, y1, x2, y2):
	return(int((x1 + x2)/2), int((y1 + y2)/2))


def find_nearest(array, value):
	array = np.asarray(array)
	idx = (np.abs(array - value)).argmin()
	#return array[idx]
	return idx


def draw_objects(img, objs, labels):
	"""Draws the bounding box and label for each object."""
	for obj in objs:
		if obj.id == 2 or obj.id == 3 or obj.id == 7:
			bbox = obj.bbox
			cv2.rectangle(img, (bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax), (0,255,0), 1)
			(label_width, label_height), baseline = cv2.getTextSize(labels.get(obj.id, obj.id), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
			cv2.rectangle(img, (bbox.xmin, bbox.ymin), (bbox.xmin + label_width + 20, bbox.ymin + 4*label_height), (0,255,0), -1)
			cv2.putText(img, '%s' % (labels.get(obj.id, obj.id).capitalize()), (bbox.xmin + 10, bbox.ymin + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1, cv2.LINE_AA)
			cv2.putText(img, '%.2f' % (obj.score), (bbox.xmin + 10, bbox.ymin + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1, cv2.LINE_AA)
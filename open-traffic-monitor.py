# Comando
#
# sudo python3 open-traffic-monitor.py
#

import time
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


def main():
	
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

	# Instanciamos el objeto Sort, que será el encargado de llevar a cabo el "tracking".
	# The Sort object type.
	tracker = Sort(max_age = 3, min_hits = 5, iou_threshold = 0.3)

	# Comenzamos a capturar el video utilizando la biblioteca OpenCV.
	videoStream = cv2.VideoCapture(config["input"]["source"])

	# Instanciamos el objeto ObjectCount, que será encargado de contar los vehículos en este caso.
	counter = ObjectCounter(videoStream)

	# Instanciamos el objeto Reporter, que será encargado de almacenar los objetos y reportarlos.
	reporter = Reporter(config["result"]["logs"])

	print('-------RESULTS--------')

	try:
		while True:		
			# Capturamos cada uno de los frames.
			ret, frame = videoStream.read()

			# Si existió un error durante la lectura del video, lo capturamos.
			if not(ret):
				print("No se pudo leer el frame.")
				break
			
			# Obtenemos el ancho y alto de la imagen de entrada.
			input_height, input_width = frame.shape[:2]

			# Tenemos que calcular el factor por el cual se debe escalar la imagen.
			scaling_factor_x = model_width / input_width
			scaling_factor_y = model_height / input_height
				
			new_frame = cv2.resize(frame, (model_height, model_width), interpolation = cv2.INTER_AREA)
			
			# Copiamos la imagen ya escalada a la entrada del tensor.
			common.set_input(interpreter, new_frame)

			start = time.perf_counter()
			interpreter.invoke()
			inference_time = time.perf_counter() - start
			objs = detect.get_objects(interpreter, config["detector"]["threshold"], (scaling_factor_x, scaling_factor_y))

			# Definimos el vector que se debe ingresar en el rastreador.
			tracked_objs = np.empty((0, 5))

			# Definimos el vector que almacenará los objetos del detector.
			detected_objs = np.empty((0, 5))

			# Definimos el vector que almacenará los objetos rastreados con sus clases.
			completed_objs = np.empty((0, 6))

			# Si se detectaron objetos, tendremos que enviarlos al tracker.
			if objs:
				for obj in objs:
					# Iteramos en todos los objetos. Solamente los compartiremos con el tracker si pertenecen a las clases "car" o "truck".
					if(obj.id == 2 or obj.id == 7):
						# Se arma el array correspondiente.
						tracked_objs = np.append(tracked_objs, np.array([[obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax, obj.score]]), axis=0)
						detected_objs = np.append(detected_objs, np.array([[obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax, obj.id]]), axis=0)
			
			# Si el array de objetos no está vacío, se lo comparte con el "tracker".
			if tracked_objs.size != 0:
				trackers = tracker.update(tracked_objs)
			# Caso contrario, como se necesita llamarlo en cada "frame", se le comparte un array vacío.
			else:
				trackers = tracker.update(np.empty((0, 5)))
			
			# Nos queda asociar el tipo de objeto con su tracker. Para ello, vamos a utiliza la distancia euclidiana.
			if trackers.size != 0:
				for track in trackers:
					tracked_box = calculate_centroid(track[0], track[1], track[2], track[3])
					for detected_obj in detected_objs:
						detected_box = calculate_centroid(detected_obj[0], detected_obj[1], detected_obj[2], detected_obj[3])
						distance = math.sqrt(pow(tracked_box[0] - detected_box[0], 2) + pow(tracked_box[1] - detected_box[1], 2))
						if distance <= 10: # Si hay una diferencia de hasta 10 píxeles, la detección se corresponde con el track.
							completed_objs = np.append(completed_objs, np.array([[track[0], track[1], track[2], track[3], track[4], detected_obj[4]]]), axis=0)
				
			# Se llama a la función para que actualice la cuenta, independientemente de si se detectó algo nuevo o no.
			objToSave = counter.update(completed_objs, config["result"]["verbose"])

			if(objToSave != None):
				reporter.data_save(objToSave)
								
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
		print("[INFO] Exiting gracefully. Bye!")
	
if __name__ == '__main__':
	main()
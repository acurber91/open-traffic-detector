# Comando
#
# python3 test6.py -m ./models/tflite/ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite -l ./models/labels/coco_labels.txt -o output_video
#

import sys
import argparse
import time
import cv2
import numpy as np
import math

from pycoral.adapters import common
from pycoral.adapters import detect
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter, run_inference
from sort.sort import Sort
from tracker.tracker import ObjectCounter
from vehicle.vehicle import Vehicle
from utils.utils import *

def main():
	# Cargamos todos los argumentos para configurar el programa.
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-m', '--model', required=True, help='File path of .tflite file')
	parser.add_argument('-l', '--labels', help='File path of labels file')
	parser.add_argument('-t', '--threshold', type=float, default=0.5, help='Score threshold for detected objects')
	parser.add_argument('-o', '--output', help='File path for the result image with annotations')
	parser.add_argument('-c', '--count', type=int, default=5, help='Number of times to run inference')
	parser.add_argument('-v', '--verbose', action='store_true', help='Increase verbosity level')
	args = parser.parse_args()

	# Se cargan el archivo de etiquetas.
	labels = read_label_file(args.labels) if args.labels else {}

	# Se declara el intérprete de TensorFlow Lite para que sea accesible desde Python. Adicionalmente, se lo
	# asocia a Edge TPU para que se encargue del procesamiento.
	interpreter = make_interpreter(args.model)

	# Asignamos memoria para el modelo de entrada de TensorFlow.
	interpreter.allocate_tensors()

	# Obtenemos los valores de ancho y alto que está esperando el modelo.
	modelSize = interpreter.get_input_details()
	modelHeight = modelSize[0]['shape'][1]
	modelWidth = modelSize[0]['shape'][2]

	# Instanciamos el objeto Sort, que será el encargado de llevar a cabo el "tracking".
	tracker = Sort(max_age=3, min_hits=5, iou_threshold=0.3)

	# Comenzamos a capturar el video utilizando la biblioteca OpenCV.
	videoStream = cv2.VideoCapture('/home/agustin/MIoT/traffic_monitor/Video01.mp4')

	# Instanciamos el objeto ObjectCount, que será encargado de contar los vehículos en este caso.
	counter = ObjectCounter(videoStream)

	print('-------RESULTS--------')

	while True:		
		# Capturamos cada uno de los frames.
		ret, frame = videoStream.read()

		# Si existió un error durante la lectura del video, lo capturamos.
		if not(ret):
			print("No se pudo leer el frame.")
			break
		
		# Obtenemos el ancho y alto de la imagen de entrada.
		inputHeight, inputWidth = frame.shape[:2]

		# Tenemos que calcular el factor por el cual se debe escalar la imagen.
		scalingFactorX = modelWidth / inputWidth
		scalingFactorY = modelHeight / inputHeight
			
		newFrame = cv2.resize(frame, (modelHeight, modelWidth), interpolation = cv2.INTER_AREA)
		
		# Copiamos la imagen ya escalada a la entrada del tensor.
		common.set_input(interpreter, newFrame)

		start = time.perf_counter()
		interpreter.invoke()
		inference_time = time.perf_counter() - start
		objs = detect.get_objects(interpreter, args.threshold, (scalingFactorX, scalingFactorY))

		# Definimos el vector que se debe ingresar en el rastreador.
		trackObjs = np.empty((0, 5))

		# Definimos el vector que almacenará los objetos del detector.
		detectedObjs = np.empty((0, 5))

		# Definimos el vector que almacenará los objetos rastreados con sus clases.
		completeObjs = np.empty((0, 6))

		# Si se detectaron objetos, tendremos que enviarlos al tracker.
		if objs:
			for obj in objs:
				# Iteramos en todos los objetos. Solamente los compartiremos con el tracker si pertenecen a las clases "car" o "truck".
				if(obj.id == 2 or obj.id == 7):
					# Se arma el array correspondiente.
					trackObjs = np.append(trackObjs, np.array([[obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax, obj.score]]), axis=0)
					detectedObjs = np.append(detectedObjs, np.array([[obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax, obj.id]]), axis=0)
		
		# Si el array de objetos no está vacío, se lo comparte con el "tracker".
		if trackObjs.size != 0:
			trackers = tracker.update(trackObjs)
		# Caso contrario, como se necesita llamarlo en cada "frame", se le comparte un array vacío.
		else:
			trackers = tracker.update(np.empty((0, 5)))
		
		# Nos queda asociar el tipo de objeto con su tracker. Para ello, vamos a utiliza la distancia euclidiana.
		if trackers.size != 0:
			for track in trackers:
				trackedBox = calculate_centroid(track[0], track[1], track[2], track[3])
				for detectedObj in detectedObjs:
					detectedBox = calculate_centroid(detectedObj[0], detectedObj[1], detectedObj[2], detectedObj[3])
					distance = math.sqrt(pow(trackedBox[0] - detectedBox[0], 2) + pow(trackedBox[1] - detectedBox[1], 2))
					if distance <= 10: # Si hay una diferencia de hasta 10 píxeles, la detección se corresponde con el track.
						completeObjs = np.append(completeObjs, np.array([[track[0], track[1], track[2], track[3], track[4], detectedObj[4]]]), axis=0)
			
		# Se llama a la función para que actualice la cuenta, independientemente de si se detectó algo nuevo o no.
		counter.update(completeObjs, args.verbose)
							
		#TODO: Tengo que implementar este método. La idea es que siempre se le compartan los IDs, para que 
		# la función se encargue de actualizar el estado de los objetos y en caso de que sea necesario eliminarlos.

		if args.output:
			draw_objects(frame, objs, labels)
			if trackers.size != 0:
				cv2.putText(frame, '%.2f' % (trackers[0, 4]), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1, cv2.LINE_AA)
			cv2.imshow(args.output, frame)
		
		# Press "q" to quit.
		if cv2.waitKey(1) == ord('q'):
			break

	# Clean up
	cv2.destroyAllWindows()
	videoStream.release()
	
if __name__ == '__main__':
	main()
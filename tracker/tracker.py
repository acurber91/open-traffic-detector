"""
Basado en https://github.com/alex-drake/OpenCV-Traffic-Counter/blob/master/trafficCounter/blobDetection.py

"""

import cv2
import datetime
import numpy as np
import json

from pycoral.adapters.detect import Object
from utils.utils import calculate_centroid
from obj.obj import ObjectToTrack

class ObjectCounter(object):
	def __init__(self, videoStream):
		self.objects = []
		self.object_count = 0
		self.objects_one_way = 0
		self.objects_other_way = 0
		self.current_frame = 0
		self.video = videoStream
		self.max_unseen_frames = 2
		self.to_delete = []		# Lista para almacenar los índices que se deben borrar.
		self.to_save = []		# Lista para almacenar los JSON de los objetos que hay que guardar.
	

	# Método para saber si el objeto ya se está contando o no.
	def check_object_counted(self, objectId):
		for obj in self.objects:
			if obj.id == objectId:
				return obj
		return None
	

	# Método para agregar nuevos objetos al conteo.
	def append_object(self, newObject):
		# Se actualizan los atributos del objeto.
		newObject.counted = True
		newObject.frames_seen += 1
		# Se lo incorpora a la lista de objetos contados y se incrementa la cantidad.
		self.objects.append(newObject)
		self.object_count += 1
	

	# Método para actualizar los frames en todos los objetos contados.
	def update_all_frames(self):
		if self.objects:
			for obj in self.objects:
				obj.frames_since_seen += 1


	# Método utilizado para eliminar un objeto de la lista de contados.
	def delete_object(self, index):
		self.objects.pop(index)
		self.object_count -= 1
	

	# Método utilizado para guardar los objetos detectados en un archivos JSON.
	def save_object(self, index):
		# Armamos el diccionario para pasar a JSON con los datos de interés.
		if(self.objects[index].speed > 0):
			y = {
				"id": str(self.objects[index].id), 
				"position": str(self.objects[index].positions[-1]),
				"timestamp": str(self.objects[index].timestamps[-1].strftime('%d/%m/%Y %H:%M:%S')),
				"direction": str(self.objects[index].direction),
				"speed": str(self.objects[index].speed),
				"class": str(self.objects[index].object_class)
				}
			#x = json.dumps(y)
			self.to_save.append(y)
	
	# Método utilizado para actualizar el estado de los objetos que han sido detectados.
	def update(self, tracked_objects, verbose):
		# Se actualiza el número de frames.
		self.current_frame = self.video.get(cv2.CAP_PROP_POS_FRAMES)
		
		# Actualizamos el estado de todos los vehículos.
		if tracked_objects.size != 0:
			for obj in tracked_objects:
				# Obtenemos el ID.
				tracked_id = int(obj[4])
				# Obtenemos la clase de objeto.
				object_class = int(obj[5])
				# Calculamos el centroide.
				new_position = calculate_centroid(obj[0], obj[1], obj[2], obj[3])
				# Y chequeamos si se está contando o no.
				search_result = self.check_object_counted(tracked_id)
				# Si no lo está, lo agregamos para que se cuente.
				if search_result is None:
					new_car = ObjectToTrack(tracked_id, object_class, new_position, self.current_frame, datetime.datetime.now())
					self.append_object(new_car)
				else:
					# Caso contrario, actualizamos todos sus parámetros.
					for obje in self.objects:
						if obje.id == search_result.id:
							obje.add_position(new_position, self.current_frame)
						# Si no se encuentra en el array, entonces 
						else:
							if obje.frame_last_seen != self.current_frame:
								obje.frames_since_seen += 1
		
		# Si el tracker no arrojó ningún resultado, a todos los objetos les incrementamos la cantidad de frames.
		else:
			self.update_all_frames()

		# Se aproveha que se llamó a la función para actualizar el estado de todos los objetos que están siendo contados.
		for obj in self.objects:
			# Primero se chequea si es necesario eliminar objetos que ya han desaparecido de la imagen.
			if obj.frames_since_seen > self.max_unseen_frames:
				self.save_object(self.objects.index(obj)) 	# ACAAAAAAAAAAAAAAAAAAAAAAAAAAA
				self.delete_object(self.objects.index(obj))
			# Luego se revisa si se puede calcular el sentido de circulación o no.
			if obj.frames_seen > 5 and obj.direction == 0:
				# Mostramos la clase de vehículo.
				print("[INFO]   Clase de objeto:", obj.object_class)
				# Declaramos un array vacío donde se almacenaran las coordenadas X de todos los centroides.
				x = []
				for p in obj.positions:
					x.append(p[0])
				if (int(obj.last_position()[0]) - int(np.mean(x))) > 0:
					obj.direction = 1 # Sentido de derecha a izquierda.
					self.objects_one_way += 1
					print("[INFO]   Sentido de circulación: ----->")
				else:
					obj.direction = 2 # Sentido de derecha a izquierda.
					self.objects_other_way += 1
					print("[INFO]   Sentido de circulación: <-----")
			
			# Ahora debemos recolectar los puntos de referencia para calcular la velocidad. Si el vehículo circula de derecha a izquierda se calcula de una manera.
			if obj.direction == 1:
				if obj.last_position()[0] > 850: # Referencia espacial (850) para asegurarse de que tenemos buenos puntos para calcular la velocidad.
					if not(obj.speed_ready):
						obj.find_references()
						if verbose:
							print("[DEBUG]  Posición A:", obj.pixel_ref["A"], ", Tiempo A:", obj.time_ref["A"])
							print("[DEBUG]  Posición B:", obj.pixel_ref["B"], ", Tiempo B:", obj.time_ref["B"])
							print("[DEBUG]  Posición C:", obj.pixel_ref["C"], ", Tiempo C:", obj.time_ref["C"])
							print("[DEBUG]  Posición D:", obj.pixel_ref["D"], ", Tiempo D:", obj.time_ref["D"])
						# Levantamos la bandera para calcular la velocidad.
						obj.speed_ready = True
			# Por otro lado, si lo hace de izquierda a derecha, se calcula de esta manera:
			elif obj.direction == 2:
				if obj.last_position()[0] < 530: # Referencia espacial (530) para asegurarse de que tenemos buenos puntos para calcular la velocidad.
					if not(obj.speed_ready):
						obj.find_references()
						if verbose:
							print("[DEBUG]  Posición A:", obj.pixel_ref["A"], ", Tiempo A:", obj.time_ref["A"])
							print("[DEBUG]  Posición B:", obj.pixel_ref["B"], ", Tiempo B:", obj.time_ref["B"])
							print("[DEBUG]  Posición C:", obj.pixel_ref["C"], ", Tiempo C:", obj.time_ref["C"])
							print("[DEBUG]  Posición D:", obj.pixel_ref["D"], ", Tiempo D:", obj.time_ref["D"])
						# Levantamos la bandera para calcular la velocidad.
						obj.speed_ready = True
			# Conociendo el sentido de circulación, se puede calcular la velocidad.
			if obj.speed_ready and obj.speed == 0:
				calculated_speed = []
				i = "A"
				j = chr(ord(i) + 1)
				if obj.direction == 2:
					while j != "E":
						distance_diff = (obj.pixel_ref[i] - obj.pixel_ref[j]) * 0.0087 # Metros por pixel.
						time_diff = abs(obj.time_ref[j].timestamp() - obj.time_ref[i].timestamp())
						try:
							velocity = (distance_diff / time_diff) * 3.6 # Para pasar de m/s a km/h.
							calculated_speed.append(round(velocity, 2))
						except ZeroDivisionError:
							calculated_speed.append(-1) # No se puede calcular la velocidad.
						i = chr(ord(i) + 1)
						j = chr(ord(j) + 1)
				elif obj.direction == 1:
					while j != "E":
						distance_diff = (obj.pixel_ref[i] - obj.pixel_ref[j]) * 0.0087 # Metros por pixel.
						time_diff = abs(obj.time_ref[i].timestamp() - obj.time_ref[j].timestamp())
						try:
							velocity = (distance_diff / time_diff) * 3.6 # Para pasar de m/s a km/h.
							calculated_speed.append(round(velocity, 2))
						except ZeroDivisionError:
							calculated_speed.append(-1) # No se puede calcular la velocidad.
						i = chr(ord(i) + 1)
						j = chr(ord(j) + 1)
				if verbose:
					print("[DEBUG]  Velocidades estimadas:", calculated_speed)
				obj.speed = round(np.average(calculated_speed), 2)
				print("[INFO]   Velocidad estimada:", obj.speed, "km/h")
				
				# Imprimimos la cantidad de objetos que se están contando.
				print("[INFO]   Cantidad de objetos:", self.object_count)
		
		# Por último, si hay objetos para salvar, los retornamos.
		if self.to_save:
			return(self.to_save.pop())
		else:
			return(None)
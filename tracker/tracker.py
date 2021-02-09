"""
Basado en https://github.com/alex-drake/OpenCV-Traffic-Counter/blob/master/trafficCounter/blobDetection.py

"""

import cv2
import datetime
import numpy as np
import json
from utils.utils import calculate_centroid
from vehicle.vehicle import Vehicle

class ObjectCounter(object):
	def __init__(self, videoStream):
		self.objects = []
		self.object_count = 0
		self.objects_one_way = 0
		self.objects_other_way = 0
		self.current_frame = 0
		self.video = videoStream
		self.max_unseen_frames = 2
	

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
			for obje in self.objects:
				obje.frames_since_seen += 1


	# Método utilizado para eliminar un objeto de la lista de contados.
	def delete_object(self, index):
		self.objects.pop(index)
		self.object_count -= 1
	
	# Método utilizado para guardar los objetos detectados en un archivos JSON.
	#def save_object(self, index):
		# Armamos el diccionario para pasar a JSON con los datos de interés.
		#y = {"id": self.objects[index].id, "position": self.positions[-1], "timestamp": self.timestamps[-1], "direction": self.direction, "speed": self.speed}
		#json.dumps(y)
		#print(y)

	
	#TODO: Tengo que implementar este método. La idea es que verifique el estado de todos los IDs, para que 
	# la función se encargue de actualizar el estado de los objetos, calcular primero el sentido de circulación,
	# luego la velocidad y en caso de que sea necesario eliminarlos cuando ya se perdieron en la pantalla.
	def update(self, trackedObjects, verboseOption):
		# Se actualiza el número de frames.
		self.current_frame = self.video.get(cv2.CAP_PROP_POS_FRAMES)
		
		# Actualizamos el estado de todos los vehículos.
		if trackedObjects.size != 0:
			for obj in trackedObjects:
				# Obtenemos el ID.
				trackedId = int(obj[4])
				# Calculamos el centroide.
				newPosition = calculate_centroid(obj[0], obj[1], obj[2], obj[3])
				# Y chequeamos si se está contando o no.
				searchResult = self.check_object_counted(trackedId)
				# Si no lo está, lo agregamos para que se cuente.
				if searchResult is None:
					newCar = Vehicle(trackedId, newPosition, self.current_frame, datetime.datetime.now())
					self.append_object(newCar)
				else:
					# Caso contrario, actualizamos todos sus parámetros.
					for obje in self.objects:
						if obje.id == searchResult.id:
							obje.add_position(newPosition, self.current_frame)
						# Si no se encuentra en el array, entonces 
						else:
							if obje.frame_last_seen != self.current_frame:
								obje.frames_since_seen += 1
		
		# Si el tracker no arrojó ningún resultado, a todos los objetos les incrementamos la cantidad de frames.
		else:
			self.update_all_frames()

		# Se realiza un loop de todos los objetos que están siendo contados.
		for obj in self.objects:
			# Primero se chequea si es necesario eliminar objetos que ya han desaparecido de la imagen.
			if obj.frames_since_seen > self.max_unseen_frames:
				#self.save_object(self.objects.index(obj))
				self.delete_object(self.objects.index(obj))
			# Luego se revisa si se puede calcular el sentido de circulación o no.
			if obj.frames_seen > 5 and obj.direction == 0:
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
			
			# Ahora debemos recolectar los puntos de referencia para calcular la velocidad.
			if obj.direction == 1:
				if obj.last_position()[0] > 850: # Referencia espacial (500) para asegurarse de que tenemos buenos puntos para calcular la velocidad.
					if not(obj.speedReady):
						obj.find_references()
						if verboseOption:
							print("[DEBUG]  Posición A:", obj.pixelRef["A"], ", Timpo A:", obj.timeRef["A"])
							print("[DEBUG]  Posición B:", obj.pixelRef["B"], ", Timpo B:", obj.timeRef["B"])
							print("[DEBUG]  Posición C:", obj.pixelRef["C"], ", Timpo C:", obj.timeRef["C"])
							print("[DEBUG]  Posición D:", obj.pixelRef["D"], ", Timpo D:", obj.timeRef["D"])
						# Levantamos la bandera para calcular la velocidad.
						obj.speedReady = True

			elif obj.direction == 2:
				if obj.last_position()[0] < 530: # Referencia espacial (850) para asegurarse de que tenemos buenos puntos para calcular la velocidad.
					if not(obj.speedReady):
						obj.find_references()
						if verboseOption:
							print("[DEBUG]  Posición A:", obj.pixelRef["A"], ", Timpo A:", obj.timeRef["A"])
							print("[DEBUG]  Posición B:", obj.pixelRef["B"], ", Timpo B:", obj.timeRef["B"])
							print("[DEBUG]  Posición C:", obj.pixelRef["C"], ", Timpo C:", obj.timeRef["C"])
							print("[DEBUG]  Posición D:", obj.pixelRef["D"], ", Timpo D:", obj.timeRef["D"])
						# Levantamos la bandera para calcular la velocidad.
						obj.speedReady = True

			if obj.speedReady and obj.speed == 0:
				calculatedSpeed = []
				i = "A"
				j = chr(ord(i) + 1)
				if obj.direction == 2:
					while j != "E":
						distanceDiff = (obj.pixelRef[i] - obj.pixelRef[j]) * 0.0087 # Metros por pixel.
						timeDiff = abs(obj.timeRef[j].timestamp() - obj.timeRef[i].timestamp())
						velocity = (distanceDiff / timeDiff) * 3.6 # Para pasar de m/s a km/h.
						calculatedSpeed.append(round(velocity, 2))
						i = chr(ord(i) + 1)
						j = chr(ord(j) + 1)
				elif obj.direction == 1:
					while j != "E":
						distanceDiff = (obj.pixelRef[i] - obj.pixelRef[j]) * 0.0087 # Metros por pixel.
						timeDiff = abs(obj.timeRef[i].timestamp() - obj.timeRef[j].timestamp())
						velocity = (distanceDiff / timeDiff) * 3.6 # Para pasar de m/s a km/h.
						calculatedSpeed.append(round(velocity, 2))
						i = chr(ord(i) + 1)
						j = chr(ord(j) + 1)
				if verboseOption:
					print("[DEBUG]  Velocidades estimadas:", calculatedSpeed)
				obj.speed = round(np.average(calculatedSpeed), 2)
				print("[INFO]   Velocidad estimada:", obj.speed, "km/h")
				
		# Imprimimos la cantidad de objetos que se están contando.
		#print(self.object_count)
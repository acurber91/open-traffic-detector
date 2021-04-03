import os
import datetime
import json
import pandas as pd
import csv

field_names = ["id", "position", "timestamp", "direction", "speed", "class"]

class Reporter():
	def __init__(self, path):
		self.path = path
		self.filename = datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
		self.full_path = self.path + self.filename + ".csv"
		self.files_reported = 0

		with open(self.full_path, 'w', newline='') as outcsv:
			writer = csv.DictWriter(outcsv, fieldnames = field_names) 
			writer.writeheader()
		outcsv.close()
		print("[INFO] Se creó el archivo:", self.full_path)


	def data_save(self, dataToSave):
		with open(self.full_path, 'a') as outcsv:
			writer = csv.DictWriter(outcsv, fieldnames = field_names)
			writer.writerow(dataToSave)
			print(datetime.datetime.now() - datetime.datetime.strptime(self.filename, '%d-%m-%Y-%H-%M-%S'))
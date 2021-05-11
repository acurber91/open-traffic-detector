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

import datetime
import csv

field_names = ["id", "position", "timestamp", "direction", "speed", "class"]

class Reporter():
	"""
	This class is used to report and log data.
	"""
	def __init__(self, path):
		self.path = path
		self.filename = datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
		self.full_path = self.path + self.filename + ".csv"
		self.files_reported = 0

		with open(self.full_path, 'w', newline='') as outcsv:
			writer = csv.DictWriter(outcsv, fieldnames = field_names) 
			writer.writeheader()
		outcsv.close()
		print("[INFO]    The following file has been created.:", self.full_path)


	def data_save(self, dataToSave):
		with open(self.full_path, 'a') as outcsv:
			writer = csv.DictWriter(outcsv, fieldnames = field_names)
			writer.writerow(dataToSave)
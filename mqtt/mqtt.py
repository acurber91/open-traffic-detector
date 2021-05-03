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

import uuid
import paho.mqtt.client as paho

class MqttClient():
    """
	This class is used to create a MQTT client and publishing and subscribing to topics.
	"""
    def __init__(self, host, port, keep_alive = 60, deviceId = str(uuid.getnode())):
        self.id = str(deviceId)
        self.host = str(host)
        self.port = int(port)
        self.keep_alive = int(keep_alive)

        # MQTT connection.
        self.client =  paho.Client(client_id = self.id, clean_session = False)

        # Setup callbacks.
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish

        # Connect.
        self.client.connect(self.host, self.port, keepalive = self.keep_alive)

        # Start loop.
        self.client.loop_start()

    def on_publish(self, client, userdata, mid):
        print("[INFO]   Successfully sent MQTT with MID: " + str(mid))

    def on_message(self, client, userdata, msg):
        """
        To be implemented.
        """

    def on_connect(self, client, userdata, flags, result_code):
        if result_code == 0:
            print("[INFO]   Successfully connected to MQTT broker.")
        else:
            print("[INFO]   Failed to connect to MQTT broker: " + paho.connack_string(result_code))

    def on_disconnect(self, client, userdata, result_code):
        print("[INFO]   Disconnected from MQTT broker.")
    
    def publish(self, topic, message, qos = 2):
        (rc, mid) = self.client.publish(str(topic), str(message), qos = qos)
    
    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
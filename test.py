# mosquitto_sub -d -h localhost -p 1883 -t "myfirst/test"
# mosquitto_pub -d -h localhost -p 1883 -t "myfirst/test" -m "This is a message sent using MQTT."
# https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php

import paho.mqtt.client as mqtt
from random import randrange, uniform
import time

client = mqtt.Client("Test")
client.connect("127.0.0.1", 1883, 60)

while True:
    randNumber = randrange(10)
    client.publish("myfirst/test", randNumber)
    print("Just published " + str(randNumber) + " to topic myfirst/test")
    time.sleep(5)
<br>
<p align="center">
    <img src="docs/header.svg" width=100%><br><br>
</p>

## About

This repository contains the **Open Traffic Detector** source code. It is a simple Python solution to track, count and estimate the speed, direction and classes of vehicles. Its main objective is to gather real-time data about traffic behaviour.

## Introduction

**Open Traffic Detector (OTD)** is a use case for edge computing applications. It is meant to run in a Raspberry Pi 4B alongside the Coral USB accelerator to perform almost real-time vehicle detection and tracking. It is designed for general tracking applications so it can be adapted to track other types of objects by fine-tunning or modifying the detector model. It uses the TensorFlow Lite library, a lightweight implementation of TensorFlow that achieves faster inference time and require less processing power. On the other hand, OpenCV is used for video processing as well as estimating the speed and direction of vehicles based on the same technique employed by VASCAR systems. This means that certain points in the image are used as references points to measure a vehicle position at a certain time to perform different calculations.

<p align="center">
    <img src="docs/readme_video.gif"><br>
</p>

### Built with

- [Python](https://www.example.com)
- [OpenCV](https://opencv.org/)
- [TensorFlow Lite](https://www.tensorflow.org/lite/)

## Install

### Hardware

As previously mentioned, OTD has been designed to run in edge computing devices. It has been successfully tested with the following hardware:

1. Ideally the [Raspberry Pi Model 4B](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/). Previous versions can also be used at some performance cost.
2. [Coral USB Accelerator](https://coral.ai/products/accelerator). This is not really mandatory but highly recommended for real-time detections.
3. A video source. This software was tested using a RTSP connection from a wireless security camera but the [Raspberry Pi Camera](https://www.raspberrypi.org/products/camera-module-v2/) or other USB camera can also be used.

### Dependencies

OTD has been designed in Python 3, so it has to be install in your system as well as the `pip` packet manager. After that, installation of required system packages can continue.

First, [Numpy](https://numpy.org/) software package has to be installed.

    $ apt-get install python3-numpy

After that [OpenCV](https://opencv.org/) package must be installed using the following command:

    $ apt-get install python3-opencv

The [Eclipse Paho MQTT](https://pypi.org/project/paho-mqtt/) client library is also required to publish generated data to a server.

    $ pip3 install paho-mqtt

At this point, the TensorFlow Lite runtime has to be installed as per the [Python Quickstart](https://www.tensorflow.org/lite/guide/python). Assuming you are running Debian Linux on a Raspberry Pi, then a new package repository has to be added and then install as follows:

    $ echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
    $ curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
    $ sudo apt-get update
    $ sudo apt-get install python3-tflite-runtime

> **NOTE**: In the near future this application will be dockerized to ease the installation process.

## Acknowledgements

- [SORT](https://github.com/abewley/sort)
- [OpenCV Traffic Counter](https://github.com/alex-drake/OpenCV-Traffic-Counter)
- [TensorFlow Lite Object Detection on Android and Raspberry Pi](https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi)
- [OpenCV Vehicle Detection, Tracking and Speed Estimation](https://www.pyimagesearch.com/2019/12/02/opencv-vehicle-detection-tracking-and-speed-estimation/)



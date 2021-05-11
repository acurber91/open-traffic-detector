<br>
<p align="center">
    <img src="docs/header.svg" width=100%><br><br>
</p>

## About

This repository contains the **Open Traffic Detector** source code. It is a simple Python solution to track, count and estimate the speed, direction and classes of vehicles. Its main objective is to gather real-time data about traffic behaviour.

## Introduction

**Open Traffic Detector** is a use case for edge computing applications. It is meant to run in a Raspberry Pi 4B alongside the Google Coral USB accelerator to perform almost real-time vehicle tracking and detection. It is designed for online tracking applications in general so it can be modified to track other types of objects by fine-tunning or adapting the detector model. It uses the TensorFlow Lite library, a lightweight implementation of TensorFlow that achieves faster inference times and requires less processing power. On the other hand, OpenCV is used for video processing as well as estimating the speed and direction of vehicles based on the same technique used by VASCAR systems. This means that points in the image are used as references to measure a vehicle position at a certain time.

### Built with

- [Python](https://www.example.com)
- [OpenCV](https://opencv.org/)
- [TensorFlow Lite](https://www.tensorflow.org/lite/)

## Dependencies

## Acknowledgements

- [SORT](https://github.com/abewley/sort)
- [OpenCV Traffic Counter](https://github.com/alex-drake/OpenCV-Traffic-Counter)
- [TensorFlow Lite Object Detection on Android and Raspberry Pi](https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi)
- [OpenCV Vehicle Detection, Tracking and Speed Estimation](https://www.pyimagesearch.com/2019/12/02/opencv-vehicle-detection-tracking-and-speed-estimation/)



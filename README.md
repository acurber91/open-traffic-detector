<br>
<p align="center">
    <img src="docs/header.svg" width=100%><br><br>
</p>

## About

This repository contains the **Open Traffic Detector** source code. It is a simple Python solution to track, count and estimate the speed, direction and classes of vehicles. Its main objective is to gather real-time data about traffic behaviour.

## Introduction

**Open Traffic Detector** is a use case for edge computing applications. It was designed to run in a Raspberry Pi 4B alongside the Google Coral USB accelerator to perform almost real-time vehicle tracking and detection. It is designed for online tracking applications so it can be modified to track other types of objects by just fine-tunning or adapting used model for the detector. It makes use of TensorFlow Lite, a lightweight implementation of TensorFlow meant to achieve faster inference times and require less processing power. OpenCV is used for video processing as well as estimating the speed and direction of the object based on the same techniques used by VASCAR systems. This means that additional calibration and measurement of references in the image have to be collected to get reliable estimations.

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



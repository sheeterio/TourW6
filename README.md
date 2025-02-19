# Virtual Tour of the W6 Faculty, PWR

This project showcases an interactive virtual tour of the L-1 building, known as "Geocentrum," home to the W6 Faculty at Wrocław University of Science and Technology (PWR). It features **562 panoramas** captured with a provisionary setup of a hacked Canon M3 camera, offering a detailed exploration of the building. 

The project is built using **Leaflet**, **Pannellum** and **Leaflet.EasyButton** libraries, which are acknowledged for their contributions to its functionality. The interface is written in **HTML**, **JavaScript**, and **CSS**. Panorama Recenter app is written in **Python**.

Direct link to access the demo of: [Virtual Tour - W6 Faculty, PWR](https://sheeterio.github.io/TourW6/)

---

## Features, update v1.1

### 1. Interactive Map
- A multi-floor map representing the layout of L-1 building.
- A point layer representing the locations of panoramas across the building.
- Users can click on points to access specific panoramas.
- Switchable button for low data panorama mode, each panorama now only is about a 200KB instead of a 5MB download, at the cost of visual quality.
- Computer and phone support, the interface is flexible to provide enough screen space for both the map and panorama viewer on any device.

### 2. Pannellum Panorama Viewer
- A seamless integration of Pannellum for viewing 360-degree panoramas.
- Smooth navigation between panorama points with next/previous buttons based on image ID key.

### 3. 3D Model Viewer
- Buttons to view 3D models of the building's interior and exterior.
- Models are hosted on Sketchfab for high-quality visualization. Each is about 15MB.

### 4. Panorama Recenter - Python program
- A simple program to help recenter panoramas to face exactly north by finding a perpendicular wall and applying a correct azimuth to it.
- User can select an input and output folder.
- Currently changing the azimuth correction requires modifying the script itself.

---

## TODO
- Street-view like movement
- Navmesh layer

---

## Installation and Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/sheeterio/TourW6
   ```
2. Run the **index.html** file within the repository. Viewing the pictures will require uploading them to some kind of a server (Pannellum limitation).

## License

**Code:** This project’s code is licensed under the MIT License. You are free to copy, modify, and distribute the code as long as the original copyright notice is retained.
**Panoramas:** All panoramas included in this project are copyrighted by the author and may not be copied, reproduced, distributed, or sold without explicit written permission.

Copyright © *2025* sheeterio
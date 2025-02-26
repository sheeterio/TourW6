# Virtual Tour of the W6 Faculty, PWR

This project showcases an interactive virtual tour of the L-1 building, known as "Geocentrum," home to the W6 Faculty at Wrocław University of Science and Technology (PWR). It features **562 panoramas** captured with a provisionary setup of a hacked Canon M3 camera, offering a detailed exploration of the building. 

The project is built using **Leaflet**, **Pannellum** and **Leaflet.EasyButton** libraries, which are acknowledged for their contributions to its functionality. The interface is written in **HTML**, **JavaScript**, and **CSS**. Panorama Recenter and Kreator Navmesh apps are written in **Python** with respective libraries.

Direct link to access the demo of: [Virtual Tour - W6 Faculty, PWR](https://sheeterio.github.io/TourW6/)

---

## Features, update v1.2

### 1. Interactive Map
- A multi-floor map representing the layout of L-1 building.
- A point layer representing the locations of panoramas across the building.
- A street-view like navigation system, click on pointers to move to the next spot.
- Users can click on points on the map to access specific panoramas quicker.
- Switchable button for low data panorama mode, each panorama now takes up about 200KB instead of being a 5MB download, at the cost of slight visual quality reduction.
- Computer and phone support, the interface is flexible to provide enough screen space for both the map and the panorama viewer on any device.

### 2. Pannellum Panorama Viewer
- A seamless integration of Pannellum for viewing 360-degree panoramas.
- Smooth navigation between panorama points with next/previous buttons based on image ID key, or with the newly added street-view movement system.

### 3. 3D Model Viewer
- Buttons to view 3D models of Geocentrum's interior and exterior.
- Models are hosted on Sketchfab for high-quality visualization. Each model is a download of about 15MB.

### 4. Panorama Recenter - Python program
- A simple program to help recenter panoramas to face exactly north (or any different direction, depending on the chosen azimuth value) by finding a perpendicular wall and applying a correct azimuth to it.
- User can select an input and output folder.

### 4. Kreator Navmesh - Python program
- Simple yet powerful solution to work with a navmesh - line layer linking panorama points.
- Ability to create and edit a navmesh based on a photo point layer.
- Support for 3 different file types: *.gpkg, .json, .geojson, .js*
- Use a helping base layer to improve navmesh's representation of reality.
- Semi-automatic creation of a navmesh by a search radius.
- Manual navmesh connection adding/removal tools.
- Visual cue tool for locating intersecting or bad navmesh connections.
- Needs to be modified to support projection systems other than EPSG:4326.

---

## TODO
- Path finding system between rooms and you - current panorama.
- Documenting the web-tour creation pipeline, possibly automating it.
- Expansion of the project to cover more buildings and areas.
- Main website hosting distinct web-tours.

---

## Installation and Usage

1. Clone this repository:
   ```bash
   git clone https://github.com/sheeterio/TourW6
   ```
2. Run the **index.html** file within the repository. Viewing the pictures will require uploading them to some kind of a server (Pannellum limitation).
3. To run the Python programs check the imports within and install them in your environment.

## License

**Code:** This project’s code is licensed under the MIT License. You are free to copy, modify, and distribute the code as long as the original copyright notice is retained.
**Panoramas:** All panoramas included in this project are copyrighted by the author and may not be copied, reproduced, distributed, or sold without explicit written permission.

Copyright © *2025* sheeterio
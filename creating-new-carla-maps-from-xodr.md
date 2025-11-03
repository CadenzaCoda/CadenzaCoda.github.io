---
date: 2025-08-12
title: 2025-08-12
draft: false
categories:
---
Turns out, it's possible to generate a map where the road is defined by waypoints AND decorate it. To achieve this, we take advantage of the OpenDriveMap (`.xodr`) files as the media to generate a map in RoadRunner, and then export to files that CARLA can ingest and export as packages. 

The instructions are as follows (for CARLA 0.9.15): 
0. Make sure you have a source-built CARLA installed. Instructions [here](https://carla.readthedocs.io/en/latest/build_carla/). 
1. If you want the road to be on a nonplanar surface, import a tif file describing the elevation map. [code]() TODO. 
2. Generate a `.xodr` file from waypoints. There is a good correspondence between the arc_length track in mpclab_common to xodr files because lines and arcs happen to be the basic building blocks of road segments in OpenDriveMap. 
3. Import xodr to Roadrunner (may be prompted to define a transformation when importing the file). Click "build scene" to convert the xodr file into actual roads in RoadRunner. 
4. Modify elevation and banking (also, add props, modify texture, ...). 
	- If you are using an elevation map defined by a tif file, select the road plan tool, and in the toolbar to the left of the canvas, click project roads. Then, if you want the road to bank according to the elevation, click on cross section tool, then select a point on the road, then in 2d editor, click "project cross section". **Repeat this for many points on the road until the road fits on the elevation map nicely.**
 	- **Alternatively**, if you just want an offroad nonplanar surface to drive on (without actual roads), after importing the elevation map, create a surface using Surface Tool, then select the surface, and check the "Sample Global Elevation" box in attributes. 
5. Export as CARLA filmbox (drop-down menu in Files) 
6. Move everything in the `Export` folder to the "Import" folder of a source-build version carla 
7. Run `make import ARGS="--package=<package_name>`
	- If you're using conda/venv, make sure you first activate the environment you've built CARLA PythonAPI with. 
8. Run `make launch` and load the map. Make sure there is at least one valid vehicle spawn point. (Can check by running `manual_control.py`. If the pygame window freezes, check to see if the spawn point is free of collision with other props/the road)  
9. Run `make package ARGS="--packages=<package_name>`. (Pay attention to the spelling!) 
	- Note: Recommend checking the map name for conflicts with existing maps. The map name is NOT the same as the package name! 
10. Move the tarball (`.tar.gz` file) from the `Dist` folder to the `Import` folder of a precompiled version carla. 
11. Run `ImportAssets.sh`, which unpacks assets of the package and moves assets 
12. Use `config.py -m <map_name>` to confirm if the import is successful. (Not package name! It's the same as whatever is shown as the level name in the unreal editor)
	- If there's a conflict with existing maps and you only want the new one, go to `CarlaUE4/Content` and remove the folders (packages) containing maps with conflicting names. 

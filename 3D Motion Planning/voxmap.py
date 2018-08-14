import numpy as np
from shapely.geometry.polygon import Polygon

def create_voxmap(data, voxel_size=5):
    """
    Returns a grid representation of a 3D configuration space
    based on given obstacle data.
    
    The `voxel_size` argument sets the resolution of the voxel map. 
    """
    # minimum and maximum north coordinates
    north_min = np.floor(np.amin(data[:, 0] - data[:, 3]))
    north_max = np.ceil(np.amax(data[:, 0] + data[:, 3]))

    # minimum and maximum east coordinates
    east_min = np.floor(np.amin(data[:, 1] - data[:, 4]))
    east_max = np.ceil(np.amax(data[:, 1] + data[:, 4]))

    # maximum altitude
    alt_max = np.ceil(np.amax(data[:, 2] + data[:, 5]))
    
    # given the minimum and maximum coordinates we can
    # calculate the size of the grid.
    north_size = int(np.ceil((north_max - north_min))) // voxel_size
    east_size = int(np.ceil((east_max - east_min))) // voxel_size
    alt_size = int(alt_max) // voxel_size

    # Create an empty grid
    voxmap = np.zeros((north_size, east_size, alt_size), dtype=np.bool)

    for i in range(data.shape[0]):
        # TODO: fill in the voxels that are part of an obstacle with `True`
        #
        # i.e. grid[0:5, 20:26, 2:7] = True
        north, east, alt, d_north, d_east, d_alt = data[i, :]
        obstacle = [
            int(north - d_north - north_min) // voxel_size,
            int(north + d_north - north_min) // voxel_size,
            int(east - d_east - east_min) // voxel_size,
            int(east + d_east - east_min) // voxel_size,
        ]

        height = int(alt + d_alt) // voxel_size
        voxmap[obstacle[0]:obstacle[1], obstacle[2]:obstacle[3], 0:height] = True

    return voxmap

def limit_value_int(value, min, max):
    return int(np.min([np.max([value, min])[0], max])[0])

def create_voxmap_in_area(data, area_center, horizontal_delta, vertical_delta, voxel_size=5):
    """
    Returns a grid representation of a 3D configuration space
    based on given obstacle data.
    
    The `voxel_size` argument sets the resolution of the voxel map. 
    """
    # minimum and maximum north coordinates
    north_min = np.floor(np.amin(data[:, 0] - data[:, 3]))
    north_max = np.ceil(np.amax(data[:, 0] + data[:, 3]))

    # minimum and maximum east coordinates
    east_min = np.floor(np.amin(data[:, 1] - data[:, 4]))
    east_max = np.ceil(np.amax(data[:, 1] + data[:, 4]))

    # maximum altitude
    alt_max = np.ceil(np.amax(data[:, 2] + data[:, 5]))
    
    # given the minimum and maximum coordinates we can
    # calculate the size of the grid.
    north_size = int(2*horizontal_delta) // voxel_size
    east_size = int(2*horizontal_delta) // voxel_size
    alt_size = int(2*vertical_delta) // voxel_size
    
    area_coordinates = [
        (area_center[0]-horizontal_delta, area_center[1]-horizontal_delta),
        (area_center[0]-horizontal_delta, area_center[1]+horizontal_delta),
        (area_center[0]+horizontal_delta, area_center[1]+horizontal_delta),
        (area_center[0]+horizontal_delta, area_center[1]-horizontal_delta),
    ]
    
    area_polygon = Polygon(area_coordinates)
    
    print("polygon area", area_polygon.area)
    
    # Create an empty grid
    voxmap = np.zeros((north_size, east_size, alt_size), dtype=np.bool)

    for i in range(data.shape[0]):
        # TODO: fill in the voxels that are part of an obstacle with `True`
        #
        # i.e. grid[0:5, 20:26, 2:7] = True
        
        north, east, alt, d_north, d_east, d_alt = data[i, :]
        obstacle = [
            int(north - d_north - north_min),
            int(north + d_north - north_min),
            int(east - d_east - east_min),
            int(east + d_east - east_min),
        ]
        
        obstacle_polygon = Polygon([
            (obstacle[0], obstacle[2]),
            (obstacle[0], obstacle[3]),
            (obstacle[1], obstacle[3]),
            (obstacle[1], obstacle[2]),
        ])
        
        # check if obstacle in area of interest
        if not area_polygon.contains(obstacle_polygon) and not area_polygon.crosses(obstacle_polygon):
            continue
        
        if not((area_center[2] - vertical_delta) < alt + d_alt < (area_center[2] + vertical_delta)):
            continue
        
        obstacle_coordinates = [
            limit_value_int(north - d_north - north_min - area_center[0] - horizontal_delta, 0, 2*horizontal_delta) // voxel_size,
            limit_value_int(north + d_north - north_min - area_center[0] - horizontal_delta, 0, 2*horizontal_delta) // voxel_size,
            limit_value_int(east - d_east - east_min - area_center[1] - horizontal_delta, 0, 2*horizontal_delta)    // voxel_size,
            limit_value_int(east + d_east - east_min  - area_center[1] - horizontal_delta, 0, 2*horizontal_delta)   // voxel_size,
        ]

        height = limit_value_int(alt + d_alt - vertical_delta, 0, 2*vertical_delta) // voxel_size
        voxmap[
            obstacle_coordinates[0]:obstacle_coordinates[1], 
            obstacle_coordinates[2]:obstacle_coordinates[3], 
            0:height
        ] = True

    return voxmap
import numpy as np
import casadi as ca
import rasterio
from rasterio.transform import Affine
from rasterio.crs import CRS
from tqdm.auto import tqdm
from typing import Callable

def export_casadi_to_tif(
    filepath: str, 
    h_func: ca.Function, 
    xmin: float, 
    xmax: float, 
    ymin: float, 
    ymax: float, 
    pixel_size_meters: float = 0.5
):
    '''
    Exports a generic CasADi surface function to a georeferenced .tif file (GeoTIFF)
    for use in applications like RoadRunner.
    
    Args:
        filepath: The path to save the file (e.g., "my_surface.tif")
        h_func: A CasADi Function that takes a 2-vector [x, y] and returns
                a scalar elevation.
        xmin: The minimum x-bound (world coordinates).
        xmax: The maximum x-bound (world coordinates).
        ymin: The minimum y-bound (world coordinates).
        ymax: The maximum y-bound (world coordinates).
        pixel_size_meters: The real-world size of each pixel (e.g., 0.5 = 50cm).
                           A smaller value means a higher resolution file.
    '''
    print(f"Exporting surface to .tif (GeoTIFF) at: {filepath}")
    print(f"Pixel size: {pixel_size_meters} meters")
    print(f"Bounds: x[{xmin}, {xmax}], y[{ymin}, {ymax}]")

    # 1. Calculate pixel dimensions based on the desired meter resolution
    width = int(np.round((xmax - xmin) / pixel_size_meters))
    height = int(np.round((ymax - ymin) / pixel_size_meters))
    
    if width == 0 or height == 0:
        print(f"Error: Calculated resolution is {width}x{height} pixels. "
              "Check pixel_size_meters or bounds.")
        return

    print(f"Calculated Resolution: {width} (x) x {height} (y) pixels")

    # 2. Define the georeferencing transform
    # This maps pixel[0,0] to the top-left corner (xmin, ymax)
    transform = Affine(pixel_size_meters, 0.0, xmin,
                       0.0, -pixel_size_meters, ymax)

    # 3. Define a custom projection (Transverse Mercator at 0,0)
    # Required by RoadRunner to prevent "No projection" error.
    custom_crs = CRS.from_dict({
        'proj': 'tmerc', 'lat_0': 0, 'lon_0': 0, 'k': 1,
        'x_0': 0, 'y_0': 0, 'units': 'm', 'datum': 'WGS84'
    })

    # 4. Generate elevation data
    # We sample at the center of each pixel
    x_coords = np.linspace(xmin + pixel_size_meters/2, xmax - pixel_size_meters/2, width)
    y_coords = np.linspace(ymax - pixel_size_meters/2, ymin + pixel_size_meters/2, height)

    elevation_array = np.zeros((height, width), dtype=np.float32)

    # The outer loop (rows) is wrapped in tqdm
    for j in tqdm(range(height), desc="Evaluating surface elevation (rows)"):
        for i in range(width):
            x_val = x_coords[i]
            y_val = y_coords[j]
            # Call the provided CasADi function
            elevation_array[j, i] = float(h_func(ca.vertcat(x_val, y_val))[0])

    # 5. Write the data to the GeoTIFF file
    print(f"Writing GeoTIFF file...")
    with rasterio.open(
        filepath,
        'w',
        driver='GTiff',
        height=elevation_array.shape[0],
        width=elevation_array.shape[1],
        count=1,
        dtype=elevation_array.dtype,
        crs=custom_crs,
        transform=transform,
    ) as dst:
        dst.write(elevation_array, 1)
        
    print(f"Successfully saved to {filepath}")


# --- HOW TO USE THIS FUNCTION ---
if __name__ == "__main__":
    
    # 1. Define your symbolic CasADi function
    x = ca.SX.sym('x')
    y = ca.SX.sym('y')
    
    # Use the "Rolling Hills" function from before
    freq_s = 25.0
    freq_y = 30.0
    h_waves = 12 * ca.cos(x / freq_s) + 10 * ca.sin(y / freq_y)
    damping_width = 100.0**2
    h_damping = ca.exp(-(x**2 + y**2) / damping_width)
    h_symbolic = h_waves * h_damping

    # Create a CasADi Function object
    # It must take a 2-vector [x, y] as input
    h_casadi_func = ca.Function('h', [ca.vertcat(x, y)], [h_symbolic])

    # 2. Define your bounds
    X_MIN = -80.0
    X_MAX = 80.0
    Y_MIN = -80.0
    Y_MAX = 80.0
    
    # 3. Call the generic export function
    export_casadi_to_tif(
        filepath='generic_surface.tif',
        h_func=h_casadi_func,
        xmin=X_MIN,
        xmax=X_MAX,
        ymin=Y_MIN,
        ymax=Y_MAX,
        pixel_size_meters=0.5
    )
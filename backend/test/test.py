import numpy as np
import netCDF4 as nc
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def find_nearest_grid_point(lon_array, lat_array, target_lon, target_lat):
    """
    Find the index of the closest point in the lon/lat arrays to the given target coordinates.

    Args:
        lon_array (np.ndarray): 2D array of longitudes from the Lambert grid.
        lat_array (np.ndarray): 2D array of latitudes from the Lambert grid.
        target_lon (float): Target longitude.
        target_lat (float): Target latitude.

    Returns:
        tuple: (i, j) indices in the array corresponding to the closest grid point.
    """
    # Convert to radians
    lon_rad = np.radians(lon_array)
    lat_rad = np.radians(lat_array)
    target_lon_rad = np.radians(target_lon)
    target_lat_rad = np.radians(target_lat)

    # Haversine formula for great-circle distance
    dlat = lat_rad - target_lat_rad
    dlon = lon_rad - target_lon_rad
    a = np.sin(dlat / 2.0)**2 + np.cos(lat_rad) * np.cos(target_lat_rad) * np.sin(dlon / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    distance = c  # Unitless, proportional to actual distance

    # Find the indices of the minimum distance
    idx = np.unravel_index(np.argmin(distance), distance.shape)
    return idx

#def ray_track(start_point, rayVectorMesh, longtitude, latitude, altitude, cloud):
def ray_track(start_point, rayVectorMesh, lat, lon, altitude, variable):
    figure = np.full((256, 256), 0) # Initialize figure with zeros

    #for i in range(rayVectorMesh.shape[0]):
    #    for j in range(rayVectorMesh.shape[1]):
    ray = rayVectorMesh[128, 128]
    ray[0] /= 110000
    ray[1] /= 110000
    encounterHeightIdx = np.argmax(altitude[altitude < start_point[2]])
    encounterHeight = altitude[encounterHeightIdx]
    factor = np.abs((start_point[2] - encounterHeight) / ray[2])
    checkPoint = start_point + factor * ray
    idxs = find_nearest_grid_point(lon, lat, checkPoint[1], checkPoint[0])
    while encounterHeightIdx > 0 and variable[encounterHeightIdx, idxs[0], idxs[1]] != -999.99:
        factor = np.abs((checkPoint[2] - altitude[encounterHeightIdx]) / ray[2])
        checkPoint = checkPoint + factor * ray
        idxs = find_nearest_grid_point(lon, lat, checkPoint[1], checkPoint[0])
        encounterHeightIdx -= 1
        print(checkPoint)

    return None


def ray_march_check_occlusion(
    ray_dirs, A, qc, qi, qr,
    lon_grid, lat_grid, alt_grid,
    threshold=0.05, max_dist_km=100, steps=100
):
    """
    ray_dirs: shape (256, 256, 3)
    A: 飛機座標 (lon, lat, alt) -> shape (3,)
    qc, qi, qr: shape (Z, Y, X)
    *_grid: shape (Z, Y, X)
    """
    H, W, _ = ray_dirs.shape
    output = np.ones((H, W), dtype=np.uint8) * 255  # 預設白色

    for i in range(H):
        for j in range(W):
            dir_vec = ray_dirs[i, j]

            for step in range(steps):
                t = step * (max_dist_km * 1000 / steps)
                pos = A + t * dir_vec  # 世界座標 (lon, lat, alt) 的近似

                # 轉換成格點 index
                z_idx = np.abs(alt_grid - pos[2]).argmin()
                y_idx = np.abs(lat_grid[0,:,0] - pos[1]).argmin()
                x_idx = np.abs(lon_grid[0,0,:] - pos[0]).argmin()

                # 確認 index 合法
                if 0 <= z_idx < qc.shape[0] and 0 <= y_idx < qc.shape[1] and 0 <= x_idx < qc.shape[2]:
                    val = qc[z_idx, y_idx, x_idx] + qi[z_idx, y_idx, x_idx] + qr[z_idx, y_idx, x_idx]
                    if val > threshold:
                        output[i, j] = 0  # 黑色（被遮擋）
                        break  # 不用再往這條 ray 走下去了

    return output  # shape (256, 256)，0=遮擋，255=可見


if __name__ == "__main__":
    # Open the netCDF file
    data = nc.Dataset("./zMcPhy.nc")
    
    aircraft = {"latitude": 34.72833251953125, "longitude": 139.1999969482422, "altitude": 5486.4}
    fujisan  = {"latitude": 35.3606583, "longitude": 138.7068067, "altitude": 3776.0}
    # Extract the variables
    lon, lat = data["longitude"], data["latitude"]
    height = np.array(data["height"])
    cloud = np.array(data["zCLMR"])
    
    # Set fill value to NaN
    cloud[cloud == -999.99] = np.nan
    
    # view_vct: the vector from aircraft to the fujisan
    view_vct = np.array([110000*(fujisan["longitude"] - aircraft["longitude"]), 110000*(fujisan["latitude"] - aircraft["latitude"]), fujisan["altitude"] - aircraft["altitude"]])
    view_vct = view_vct / np.linalg.norm(view_vct)
    # right_vct: the vector f cross z
    right_vct = np.cross(view_vct, np.array([0, 0, 1]))
    right_vct = right_vct / np.linalg.norm(right_vct)
    # up_vct: the vector r cross f
    up_vct = np.cross(right_vct, view_vct)
    up_vct = up_vct / np.linalg.norm(up_vct)

    print("forward vector: ", up_vct)
    print("right vector: ", right_vct)
    print("view vector: ", view_vct)
    grid_index_mesh = np.meshgrid(np.arange(0, 256), np.arange(0, 256))

    x_angle = (grid_index_mesh[0] - 128) / 128 * 45  # degrees
    y_angle = (128 - grid_index_mesh[1]) / 128 * 45  # degrees（注意 y 軸通常向下）

    x_offset = np.tan(np.deg2rad(x_angle))[..., None]
    y_offset = np.tan(np.deg2rad(y_angle))[..., None]

    ray_dirs = view_vct + x_offset * right_vct + y_offset * up_vct
    ray_dirs /= np.linalg.norm(ray_dirs, axis=-1, keepdims=True)  # normalize

    idx = find_nearest_grid_point(lon, lat, aircraft["longitude"], aircraft["latitude"])

    ray_track([aircraft["latitude"], aircraft["longitude"], aircraft["altitude"]], ray_dirs, lat, lon, height, cloud)
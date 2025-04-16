import numpy as np
import netCDF4 as nc
import xarray as xr
import matplotlib.pyplot as plt
#import cartopy.crs as ccrs
#import cartopy.feature as cfeature
from scipy.spatial import cKDTree

def find_nearest_grid_indices(worldx, worldy, points):
    nx, ny = worldx.shape

    # Step 1: Flatten worldx, worldy to (N, 2)
    grid_points = np.column_stack((worldx.ravel(), worldy.ravel()))  # shape: (nx*ny, 2)

    # Step 2: Extract x,y from points, reshape to (256*256, 2)
    point_xy = points[..., :2].reshape(-1, 2)

    # Step 3: Use KDTree to find nearest neighbors
    tree = cKDTree(grid_points)
    dist, idx_flat = tree.query(point_xy)  # idx_flat: (256*256,)

    # Step 4: Convert flat indices back to (i, j)
    i_indices, j_indices = np.unravel_index(idx_flat, (nx, ny))  # shape: (256*256,)

    # Step 5: reshape back to (256, 256)
    i_indices = i_indices.reshape(256, 256)[..., np.newaxis]
    j_indices = j_indices.reshape(256, 256)[..., np.newaxis]
    

    return i_indices, j_indices

def find_nearest_grid_point(lat_array, lon_array, target_lat, target_lon):
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
    latIdx, lonIdx = idx[0], idx[1]
    return latIdx, lonIdx

def ray_track_topo(start_point, rayVectorMesh, 
              worldx, worldy, worldz, topo, longitude, latitude):
    figure = np.full((256, 256), -999.99) # Initialize figure with zeros

    # start_point shape to (256, 256, 3)
    start_point = np.expand_dims(start_point, axis=(0, 1))
    #for i in range(rayVectorMesh.shape[0]):

    startHeightIdx = np.argmax(worldz[worldz < start_point[0, 0, 2]])
    startHeight = worldz[startHeightIdx]
    idx = 129
    factor = - (start_point[0, 0, 2] - startHeight) / rayVectorMesh[:, :, [2]] # shape (256, 256)
    downwardRayMask = rayVectorMesh[:, :, 2] < 0

    checkPoints = start_point + factor * rayVectorMesh # (256, 256, 3)

    i_indices, j_indices = find_nearest_grid_indices(worldx, worldy, checkPoints)
    while startHeightIdx > 0:
        print(startHeightIdx)
        currentHeight = worldz[startHeightIdx]
        for i in range(figure.shape[0]):
            for j in range(figure.shape[1]):
                if currentHeight <= topo[i_indices[i, j], j_indices[i, j]] and figure[i, j] == -1:
                    figure[i, j] = topo[i_indices[i, j], j_indices[i, j]]
        #figure[np.logical_and((currentHeight <= topo[i_indices, j_indices])[:, :, 0], figure == 0)] = currentHeight
        figure[np.logical_and(downwardRayMask, figure == -999.99)] = -1
        factor = - 500 / rayVectorMesh[:, :, [2]]
        checkPoints = checkPoints + factor * rayVectorMesh
        i_indices, j_indices = find_nearest_grid_indices(worldx, worldy, checkPoints)
        startHeightIdx -= 1
    plt.contourf(figure[::-1, :], vmin=-999.99, vmax=2100)#, shading='auto')
    plt.colorbar()
    plt.scatter(128, 128, c='red', zorder=3)
    plt.savefig(f"topo-aircraft.jpg", dpi=300)
    plt.clf()

#def ray_track(start_point, rayVectorMesh, longtitude, latitude, altitude, cloud):
def ray_track(start_point, rayVectorMesh, 
              worldx, worldy, worldz, variable, longitude, latitude):
    figure = np.full((256, 256), 0) # Initialize figure with zeros

    # start_point shape to (256, 256, 3)
    start_point = np.expand_dims(start_point, axis=(0, 1))
    #for i in range(rayVectorMesh.shape[0]):

    startHeightIdx = np.argmax(worldz[worldz < start_point[0, 0, 2]])
    startHeight = worldz[startHeightIdx]
    factor = np.abs((start_point[:, : 2] - startHeight) / rayVectorMesh[:, :, [2]]) # shape (256, 256)
    checkPoints = start_point + factor * rayVectorMesh # (256, 256, 3)
    i_indices, j_indices = find_nearest_grid_indices(worldx, worldy, checkPoints)
    plt.pcolormesh(worldx, worldy, variable[startHeightIdx] >= 1e-6, shading='auto')
    plt.savefig("test.jpg", dpi=300)
    plt.clf()
    plt.pcolormesh(variable[startHeightIdx, i_indices, j_indices][:, :, 0] >= 1e-6, shading='auto')
    plt.savefig("test2.jpg", dpi=300)
    #kidx = startHeightIdx
    #print(variable.shape)
    #print(variable[startHeightIdx, i_indices, j_indices].shape)
    #while kidx > 0:
    #    variableStatus = variable[kidx, i_indices, j_indices]


    #for ipx in range(256):
    #    for jpx in range(256):
    #        ray = rayVectorMesh[ipx, jpx]
    #        # if the ray is upward, figure = -999.99 and skip
    #        if ray[ipx, jpx][2] >= 0: 
    #            figure[ipx, jpx] = -999.99
    #            continue
    #        kidx = startHeightIdx
    #        idx, jdx = find_nearest_grid_point(longitude, latitude, checkPoints[ipx, jpx, 1], checkPoints[ipx, jpx, 0])
    #        gridStatus = variable[kidx, idx, jdx]
    #        while kidx > 0 and gridStatus != -999.99:
    #            # check gridStatus to stop by existence of variable or keep moving
    #            if gridStatus >= 1e-6: 
    #                figure[ipx, jpx] = gridStatus
    #                break
    #            # update checkPoint
    #            else:
    #                checkPoints[ipx, jpx, :] = checkPoints[ipx, jpx, :] + ray * (worldz[kidx] - worldz[kidx - 1])
    #            # check boundary then update gridStatus


                
 
            



    #print(checkPoint[idx, idx, :])
    #print(worldx[i_indices[idx, idx], j_indices[idx, idx]], worldy[i_indices[idx, idx], j_indices[idx, idx]])
    
    #latIdx, lonIdx = find_nearest_grid_point(lat, lon, checkPoint[0], checkPoint[1])
    #while encounterHeightIdx > 0 and variable[encounterHeightIdx, latIdx, lonIdx] != -999.99:
    #    factor = np.abs((checkPoint[2] - altitude[encounterHeightIdx]) / ray[2])
    #    checkPoint = checkPoint + factor * ray
    #    latIdx, lonIdx = find_nearest_grid_point(lat, lon, checkPoint[1], checkPoint[0])
    #    encounterHeightIdx -= 1
    #    print(checkPoint, variable[encounterHeightIdx, latIdx, lonIdx])

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
    data = nc.Dataset("./zMcPhy17.nc")
    
    aircraft = {"latitude": 34.72833251953125, "longitude": 139.1999969482422, "altitude": 5486.4}
    fujisan  = {"latitude": 35.3606583, "longitude": 138.7068067, "altitude": 1500, "x": 0, "y": 0} #3776.0}
    aircraft["x"] = 110000 * (aircraft["longitude"] - fujisan["longitude"])
    aircraft["y"] = 110000 * (aircraft["latitude"] - fujisan["latitude"])

    lon, lat = np.array(data["longitude"]), np.array(data["latitude"])
    worldx = 110000 * (lon - fujisan["longitude"])
    worldy = 110000 * (lat - fujisan["latitude"])
    worldz = np.array(data["height"])
    worldz = np.array([-10] + [x for x in worldz])
    cloud = np.array(data["zCLMR"])
    topo = np.array(data["topo"])
    print(np.unique(topo))
    
    # Set fill value to NaN
    cloud[cloud == -999.99] = np.nan
    
    # view_vct: the vector from aircraft to the fujisan
    view_vct = np.array([fujisan["x"] - aircraft["x"], fujisan["y"] - aircraft["y"], fujisan["altitude"] - aircraft["altitude"]])
    view_vct = view_vct / np.linalg.norm(view_vct)
    # right_vct: the vector f cross z
    right_vct = np.cross(view_vct, np.array([0, 0, 1]))
    right_vct = right_vct / np.linalg.norm(right_vct)
    # up_vct: the vector r cross f
    up_vct = np.cross(right_vct, view_vct)
    up_vct = up_vct / np.linalg.norm(up_vct)

    print("up    vector: ", up_vct)
    print("right vector: ", right_vct)
    print("view  vector: ", view_vct)
    grid_index_mesh = np.meshgrid(np.arange(0, 256), np.arange(0, 256))

 
    xViewDegree = 90
    yViewDegree = 20
    x_angle = (grid_index_mesh[0] - 128) / 128 * (xViewDegree / 2)  # degrees
    y_angle = (128 - grid_index_mesh[1]) / 128 * (yViewDegree / 2)  # degrees（注意 y 軸通常向下）
    x_offset = np.tan(np.deg2rad(x_angle))[..., None]
    y_offset = np.tan(np.deg2rad(y_angle))[..., None]

    ray_dirs = view_vct + x_offset * right_vct + y_offset * up_vct
    ray_dirs /= np.linalg.norm(ray_dirs, axis=-1, keepdims=True)  # normalize
    print(np.max(ray_dirs[:, :, 2]))

    ray_track_topo([aircraft["x"], aircraft["y"], aircraft["altitude"]], ray_dirs, 
              worldx, worldy, worldz, topo, lon, lat)
    #ray_track([aircraft["x"], aircraft["y"], aircraft["altitude"]], ray_dirs, 
    #           worldx, worldy, worldz, cloud, lon, lat)
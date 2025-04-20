import numpy as np
import netCDF4 as nc
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.cm import get_cmap
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

def ray_track_topo(start_point, rayVectorMesh, 
              worldx, worldy, worldz, topo, figsize=(256, 256)):
    figure = np.full((figsize[0], figsize[1]), -9999.99) # Initialize figure with zeros

    # start_point shape to (256, 256, 3)
    start_point = np.expand_dims(start_point, axis=(0, 1))

    startHeightIdx = np.argmax(worldz[worldz < start_point[0, 0, 2]])
    startHeight = worldz[startHeightIdx]
    factor = - (start_point[0, 0, 2] - startHeight) / rayVectorMesh[:, :, [2]] # shape (256, 256)
    downwardRayMask = rayVectorMesh[:, :, 2] < 0

    checkPoints = start_point + factor * rayVectorMesh # (256, 256, 3)

    i_indices, j_indices = find_nearest_grid_indices(worldx, worldy, checkPoints)
    while startHeightIdx > 0:
        print("Compute topo: ", startHeightIdx)
        currentHeight = worldz[startHeightIdx]
        for i in range(figure.shape[0]):
            for j in range(figure.shape[1]):
                if currentHeight <= topo[i_indices[i, j], j_indices[i, j]] and figure[i, j] == -1:
                    figure[i, j] = topo[i_indices[i, j], j_indices[i, j]]
        figure[np.logical_and(downwardRayMask, figure == -9999.99)] = -1
        factor = - (worldz[startHeightIdx] - worldz[startHeightIdx-1]) / rayVectorMesh[:, :, [2]]
        checkPoints = checkPoints + factor * rayVectorMesh
        i_indices, j_indices = find_nearest_grid_indices(worldx, worldy, checkPoints)
        startHeightIdx -= 1
    return figure

def ray_track(start_point, rayVectorMesh, 
              worldx, worldy, worldz, variable, figsize=(256, 256)):
    figure = np.full((figsize[0], figsize[1]), -9999.99) # Initialize figure with zeros
    # start_point shape to (256, 256, 3)
    start_point = np.expand_dims(start_point, axis=(0, 1))

    startHeightIdx = np.argmax(worldz[worldz < start_point[0, 0, 2]])
    startHeight = worldz[startHeightIdx]
    factor = - (start_point[0, 0, 2] - startHeight) / rayVectorMesh[:, :, [2]] # shape (256, 256)
    upRayMask = rayVectorMesh[:, :, 2] >= 0

    checkPoints = start_point + factor * rayVectorMesh # (256, 256, 3)

    i_indices, j_indices = find_nearest_grid_indices(worldx, worldy, checkPoints)
    while startHeightIdx > 0:
        print("Compute cloud: ", startHeightIdx)
        currentHeight = worldz[startHeightIdx]
        figure[np.logical_and(variable[startHeightIdx, i_indices, j_indices][:, :, 0] > 1e-4, figure == -9999.99)] = -currentHeight
        factor = - (worldz[startHeightIdx] - worldz[startHeightIdx-1]) / rayVectorMesh[:, :, [2]]
        checkPoints = checkPoints + factor * rayVectorMesh
        i_indices, j_indices = find_nearest_grid_indices(worldx, worldy, checkPoints)
        startHeightIdx -= 1
    figure[upRayMask] = -9999.99
    return figure

def getRayMesh(start_point, end_point, figsize=(256, 256), xViewDegree=90, yViewDegree=20):
    # view_vct: the vector from aircraft to the fujisan
    view_vct = np.array([end_point["x"] - start_point["x"], end_point["y"] - start_point["y"], end_point["altitude"] - start_point["altitude"]])
    view_vct = view_vct / np.linalg.norm(view_vct)
    # right_vct: the vector f cross z
    right_vct = np.cross(view_vct, np.array([0, 0, 1]))
    right_vct = right_vct / np.linalg.norm(right_vct)
    # up_vct: the vector r cross f
    up_vct = np.cross(right_vct, view_vct)
    up_vct = up_vct / np.linalg.norm(up_vct)

    grid_index_mesh = np.meshgrid(np.arange(0, figsize[0]), np.arange(0, figsize[1]))
 
    x_angle = (grid_index_mesh[0] - figsize[0]//2) / (figsize[0]//2) * (xViewDegree / 2)  # degrees
    y_angle = (figsize[0]//2 - grid_index_mesh[1]) / (figsize[0]//2) * (yViewDegree / 2)  # degrees（注意 y 軸通常向下）
    x_offset = np.tan(np.deg2rad(x_angle))[..., None]
    y_offset = np.tan(np.deg2rad(y_angle))[..., None]

    ray_dirs = view_vct + x_offset * right_vct + y_offset * up_vct
    ray_dirs /= np.linalg.norm(ray_dirs, axis=-1, keepdims=True)  # normalize
    return ray_dirs

def calculate_view_image(start_point, end_point, model_path, 
                         figsize=(256, 256), xViewDegree=90, yViewDegree=20):

    start_point["x"] = 110000 * (start_point["longitude"] - end_point["longitude"])
    start_point["y"] = 110000 * (start_point["latitude"] - end_point["latitude"])
    
    nc_data = nc.Dataset(f"{model_path}")
    lon, lat = np.array(nc_data["longitude"]), np.array(nc_data["latitude"])
    # to meter coordinate with end point as origin point (0, 0, height)
    worldx = 110000 * (lon - end_point["longitude"])
    worldy = 110000 * (lat - end_point["latitude"])
    worldz = np.array(nc_data["height"])
    worldz = np.array([-10] + [x for x in worldz])
    considerVar = np.array(nc_data["zCLMR"])
    considerVar[considerVar == -9999.99] = np.nan
    topo = np.array(nc_data["topo"])

    # calculate the ray directions
    ray_dirs = getRayMesh(aircraft, fujisan, figsize=(256, 256))

    # calculate the ray tracing for topography and variable
    topoView = ray_track_topo([aircraft["x"], aircraft["y"], aircraft["altitude"]], ray_dirs, 
              worldx, worldy, worldz, topo)
    cloudView = ray_track([aircraft["x"], aircraft["y"], aircraft["altitude"]], ray_dirs,
               worldx, worldy, worldz, considerVar)
    return topoView, cloudView

def generateFigure(topoView, cloudView, output_path):
    # Define levels
    special_value = -9999.99
    topo_levels = np.arange(0, 3500 + 100, 100)    # 0 to 2500 in 100m steps

    # Combine all levels
    all_bounds = np.concatenate(([special_value], topo_levels))
    # Remove duplicate if -500 is already in topo_levels
    all_bounds = np.unique(all_bounds)

    # Create colors
    # Blue for special value
    colors = ['blue']

    # Terrain colors for topography (sampled from 'terrain' colormap)
    terrain_cmap = get_cmap('terrain', len(topo_levels) - 1)
    terrain_colors = [terrain_cmap(i) for i in range(len(topo_levels) - 1)]
    colors.extend(terrain_colors)

    # Create colormap and norm
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(all_bounds, ncolors=cmap.N+2, extend='both')

    fig, ax = plt.subplots()
    plt.pcolormesh(topoView[::-1], cmap=cmap, norm=norm)
    plt.pcolormesh(np.ma.masked_array(cloudView[::-1], cloudView[::-1]==-9999.99), cmap='grey_r', vmin=0, vmax=1)
    #plt.scatter(topoView.shape[0]//2, topoView.shape[1]//2, c="red", s=5)
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(f"{output_path}/merge-aircraft.jpg", dpi=300)

#if __name__ == "__main__":
#    # Open the netCDF file
#    nc_path = "../tmp/nc/20250409_170000_alt.nc"
#    #data = nc.Dataset("../test/zMcPhy17.nc")
#    
#    aircraft = {"latitude": 34.72833251953125, "longitude": 139.1999969482422, "altitude": 5486.4}
#    fujisan  = {"latitude": 35.3606583,        "longitude": 138.7068067, "altitude": 1500, "x": 0, "y": 0}
#    topoView, cloudView = calculate_view_image(start_point=aircraft, end_point=fujisan, model_path=nc_path)
#    generateFigure(topoView, cloudView)
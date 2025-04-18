from fastapi import APIRouter, HTTPException
import numpy as np
from scipy.spatial import cKDTree
import netCDF4 as nc
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.cm import get_cmap
from pathlib import Path
from utils.pres2alt import tranform_nc_file
from param_store import get_param
import logging
from pydantic import BaseModel


logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler(f"{Path(__file__).parent.parent}/log/view_calculation_handler.log")  # Log to a file
    ]
)
router = APIRouter()

class UserParams(BaseModel):
    start_point_longitude: float
    start_point_latitude: float

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


#@router.post("/generate-tmp-model-data")
#def generate_weather_data(params: UserParams):
#    try:
#        home_path = Path(__file__).parent.parent
#        year  = params.year
#        month = params.month
#        day   = params.day
#        hour  = params.hour
#
#        file_date = f"{year:04d}{month:02d}{day:02d}_{hour:02d}0000"
#        input_path = home_path / "data" / "own" / f"{file_date}.nc"
#        output_path = home_path / "tmp" / "nc" / f"{file_date}_alt.nc"
#
#        if not input_path.exists():
#            logging.error(f"Input file {input_path} does not exist.")
#            raise HTTPException(status_code=404, detail=f"Input file {input_path} does not exist.")
#        if not output_path.parent.exists():
#            logging.info(f"Creating output directory: {output_path.parent}")
#            output_path.parent.mkdir(parents=True, exist_ok=True)
#        if output_path.exists():
#            logging.info(f"Weather data already generated: {output_path}")
#            return {"message": "Weather data already generated", "output_path": str(output_path)}
#
#        tranform_nc_file(input_path, output_path)
#        logging.info(f"Weather data generated successfully: {output_path}")
#        return {"message": "Weather data generated successfully", "output_path": str(output_path)}
#
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))